import openpyxl
import json
import re

import argparse
import textwrap # Used in the Argument Help Text
from colorama import Fore, Style # Used in the Argument Help Text

# Arguments Parsing - Use -h or --help to display this help text

description = textwrap.dedent(f"""\
        {Fore.BLUE}{Style.BRIGHT}RACF Certificate Processing Utility for IBM Concert (RACFCerts2Concert){Style.RESET_ALL}

        This script processes RACF data extracted using IRRDBU00 into a local text file and
        generates output in both Excel (optional) and JSON formats to upload to the IBM Concert product.

        {Fore.GREEN}{Style.BRIGHT}Processing Steps:{Style.RESET_ALL}
        1. {Fore.CYAN}Filtering for record types:{Style.RESET_ALL} Only a subset of fields from RACF records 0207, 0500, 0560, 0561, 1560 are processed.
        2. {Fore.CYAN}Remove Not Trusted Certificates:{Style.RESET_ALL}  Certificates with NOTRUST are removed.
        3. {Fore.CYAN}Remove DIGTRING records:{Style.RESET_ALL}  RACF entries for class DIGTRING are removed.
        4. {Fore.CYAN}Transformation:{Style.RESET_ALL} Combines relevant fields from all RACF records into a single line for each certificate by CERT_NAME.
        5. {Fore.CYAN}Output Generation:{Style.RESET_ALL}
           - {Fore.YELLOW}Excel (optional):{Style.RESET_ALL} Creates an Excel file with all relevant processed fields.
           - {Fore.YELLOW}JSON:{Style.RESET_ALL} Creates a JSON file with all certificates to upload into IBM Concert in a single environment.

        {Fore.RED}{Style.BRIGHT}Example Usage:{Style.RESET_ALL}
        python RACFCerts2Concert.py -i RACF_DATA.txt -o RACF_Certificates.json -x RACF_Certificates.xlsx -e zos_certificates --lpar ESYSMVS.MVS1
        python RACFCerts2Concert.py -i RACF_DATA.txt -o RACF_Certificates.json -e zos_certificates  --lpar ESYSMVS.MVS1 (Without Excel output)

        """)

parser = argparse.ArgumentParser(
    description=description,
    formatter_class=argparse.RawDescriptionHelpFormatter  # Keep the formatting
)

#parser = argparse.ArgumentParser(description="Processes the RACF Certificate Data \n and output files formatted for Excel for reference, and JSON to upload into IBM Concert.")
parser.add_argument("-i", "--input", help="Path to the input RACF IRRDBU00 text file.")
parser.add_argument("-o", "--output_json", help="Path to the output JSON file.", default="RACFCerts2Concert.json")
parser.add_argument("-e", "--env_name", help="IBM Concert Environment Name", default="zos_certificates")
parser.add_argument("-l", "--lpar", help="z/OS SYSPLEX.LPAR Name (used for username@SYSPLEX.LPAR)", default="MVS1")
parser.add_argument("-x", "--output_excel", help="Path to the output Excel file. (Optional)", default=None)
args = parser.parse_args()

input_file = args.input

record_definitions = {
    "0500": [
        {"name": "CERT_NAME", "start": 6, "end": 251},
        {"name": "CREATE_DATE", "start": 271, "end": 280},
        {"name": "UACC", "start": 337, "end": 344}
    ],
    "1560": [
        {"name": "CERT_NAME", "start": 6, "end": 251},
        {"name": "ISSUER_DN", "start": 262, "end": 1285},
        {"name": "SUBJECT_DN", "start": 1287, "end": 2310},
        {"name": "SIG_ALG", "start": 2312, "end": 2327},
        {"name": "CERT_FGRPRNT", "start": 2329, "end": 2392}
    ],
    "0560": [
        {"name": "CERT_NAME", "start": 6, "end": 251},
        {"name": "START_DATE", "start": 262, "end": 271},
        {"name": "START_TIME", "start": 273, "end": 280},
        {"name": "END_DATE", "start": 282, "end": 291},
        {"name": "END_TIME", "start": 293, "end": 300}
    ],
    "0561": [
        {"name": "CERT_NAME", "start": 6, "end": 251},
        {"name": "RING_NAME", "start": 262, "end": 507},
    ],
    "0207": [
        {"name": "USER_NAME", "start": 6, "end": 13},
        {"name": "CERT_NAME", "start": 15, "end": 260},
        {"name": "CERTLABL", "start": 262, "end": 293}
    ],
    "0562": [
        {"name": "CERT_NAME", "start": 262, "end": 507},
        {"name": "CERT_USAGE", "start": 509, "end": 516},
        {"name": "KEYR_NAME", "start": 6, "end": 251}
    ],
}

data = {}

with open(input_file, 'r') as infile:

    for line in infile:

        if not line:  # Skip empty lines
            continue

        record_type = line[:4]

        if record_type not in record_definitions:
            print(f"Warning: Unknown record type '{record_type}' found. Skipping line.")
            continue

        record_data = {}

        for field_def in record_definitions[record_type]:
            start = field_def["start"] - 1  # Adjust to 0-based indexing
            end = field_def["end"]
            field_value = line[start:end].strip()
            record_data[field_def["name"]] = field_value

        name = record_data.get("CERT_NAME", "")

        if name not in data:
            data[name] = {}  # Initialize dictionary for the name if not exists

        # Store all fields with record_type prefix
        for field_name, field_value in record_data.items():
            if field_name != "CERT_NAME": # Avoid duplicating the NAME field
                data[name][f"{record_type}_{field_name}"] = field_value


print(f"Successfully processed RACF Certificated Data")

# --- Processing Data ---

# Step 1.1: Filter Certificates that do not have records in 0207 (these are DIGTRING instead of DIGTCERT that comes from 0560)
# Step 1.2: Remove Untrusted Certificates (0500_UACC = NOTRUST) as these are not valid
filtered_data = {}
for name, record_data in data.items():
    if "0207_USER_NAME" in record_data:
        if record_data["0500_UACC"] != "NOTRUST":
            filtered_data[name] = record_data

data = filtered_data

# Step 2: Create new filed with the metadata needed by Concert data for all certificates
for name, record_data in data.items():
    data[name]["LPAR"] = args.lpar
    data[name]["validity_start_date"] = data[name]["0560_START_DATE"] + " " + data[name]["0560_START_TIME"] + " -0400 UTC"
    data[name]["validity_end_date"] = data[name]["0560_END_DATE"] + " " + data[name]["0560_END_TIME"] + " -0400 UTC"


# Processing data to Save as Excel file (Optional Step, depending on arguments)
# Appending rows for Excel formatting

if args.output_excel:

    output_data = []

    for name, record_data in data.items():
        row = {"CERT_NAME": name}
        row.update(record_data)  # Add all other fields to the row
        output_data.append(row)

    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Dynamically determine fieldnames from all collected data.
    fieldnames = ["CERT_NAME"]
    for row in output_data:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    # Write header row
    worksheet.append(fieldnames)

    # Write data rows
    for row_data in output_data:
        row_values = [row_data.get(field, "") for field in fieldnames]  # Handle missing fields
        worksheet.append(row_values)


    workbook.save(args.output_excel)
    print(f"Successfully wrote Excel data to '{args.output_excel}'")

# --- Prepare data for JSON writing ---
json_output = {"components": []}
for name, record_data in data.items():

    serial_number = record_data.get('1560_CERT_FGRPRNT', "")

    component = {
        "type": "certificate",
        "ref": "certificate:" + serial_number,  # Use .get()
        "serial_number": serial_number,      # Use .get()
        "properties": [
            {
                "name": "subject",
                "value": record_data.get("1560_SUBJECT_DN", "").replace("'", "")             # Use .get()
            },
            {
                "name": "issuer",
                "value": record_data.get("1560_ISSUER_DN", "")                  # Use .get()
            },
            {
                "name": "description",
                "value": record_data.get("0207_CERTLABL", "")                  # Use .get()
            },
            {
                "name": "validity_start_date",
                "value": record_data.get("0560_START_DATE", "") + " " + record_data.get("0560_START_TIME", "") + " -0400 UTC"
            },
            {
                "name": "validity_end_date",
                "value": record_data.get("0560_END_DATE", "") + " " + record_data.get("0560_END_TIME", "") + " -0400 UTC"
            },
            {
                "name": "owner",
                "value": record_data.get("0207_USER_NAME", "") + "@" + args.lpar
            },
            {
                "name": "namespace",
                "value": args.lpar
            },
            {
                "name": "dns_names",
                "value": args.lpar
            },
            {
                "name": "certificate_type",
                "value": "IBM z/OS RACF " + record_data.get("0562_CERT_USAGE", "") + " " + record_data.get("1560_SIG_ALG", "")
            },
            {
                "name": "metadata",
                "value": "{\"cert_name\": \"" + name +  "\", "
                "          \"keyring\": \"" + record_data.get("0561_RING_NAME", "") +  "\", "
                "          \"certificate_host\": \"" + args.lpar +  "\", "
                "          \"rna\": true, "                                                             # Must be true to invoke the automated Workflow!
                "          \"api_server\": \"" + args.lpar + ".ibm.com" +  "\", "                                                             # Used together with Namespace in the logic to replace missing certificates
                "          \"rna_service\": \"" +  record_data.get("0207_CERTLABL", "") +  "\", "       # These are additional free-text fields
                "          \"rna_file\": \"" +  name +  "\", "                                          # These are additional free-text fields
                "          \"cert_label\": \"" + record_data.get("0207_CERTLABL", "") + "\"}"           # Non-standard fields are not yet included in the Workflow call, will be fixed in Concert 1.1
            },
        ]
    }

    json_output["components"].append(component)


# --- Prepare data for JSON writing (dependencies) ---
depends_on_list = []
for name, record_data in filtered_data.items():
    if "1560_CERT_FGRPRNT" in record_data:  # Check if the key exists
        depends_on_list.append(f"certificate:{record_data['1560_CERT_FGRPRNT']}")

json_output["dependencies"] = [
    {
        "ref": f"environment:{args.env_name}",
        "depends_on": depends_on_list
    }
]

with open(args.output_json, 'w') as outfile:
    json.dump(json_output, outfile, indent=2)  # Use indent for readability
print(f"Successfully wrote JSON data to '{args.output_json}'")