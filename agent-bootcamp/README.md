# IPL-check Custom Agent for watsonx Orchestrate

This directory contains a custom agent implementation for watsonx Orchestrate that validates z/OS system health after an Initial Program Load (IPL). The agent performs automated checks to ensure systems are properly configured and operational.

## 📁 Directory Structure

```
custom-agent2/
├── agents/
│   └── IPL-check.yaml          # Main agent configuration
├── tools/
│   ├── operatorCommand.yaml    # z/OSMF Console API tool
│   └── tsoCommand.yaml         # z/OSMF TSO API tool
└── README.md                   # This file
```

## 📄 File Descriptions

### `agents/IPL-check.yaml`

The main agent configuration file that defines the IPL validation agent.

**Key Components:**
- **Name**: `IPL_Validator`
- **Type**: Native agent (`kind: native`)
- **LLM**: Uses `watsonx/meta-llama/llama-3-3-70b-instruct`
- **Style**: React-based reasoning
- **Tools**: Integrates with `sendOperatorCommand` and `executeTsoCommand`

**Validation Steps:**
1. **IPL Pack Verification**: Issues `D IPLINFO` operator command to verify the correct IPL pack is loaded and extracts the CURRENT IPL DEVICE value
2. **TSO Status Check**: Executes TSO `TIME` command to confirm TSO subsystem is running (looks for "READY" message)
3. **OMVS Status Check**: Issues `D OMVS` operator command to verify OMVS (Unix System Services) is running
4. **OMVS Mount Verification**: Issues `D OMVS,MF` operator command to check for any mount failures in OMVS

**Instructions Logic:**
The agent follows a sequential workflow, reporting each step's purpose and output to the user in a clear, formatted manner.

### `tools/operatorCommand.yaml`

OpenAPI specification for z/OSMF REST Console Services API.

**Purpose**: Enables the agent to issue MVS operator commands through the z/OSMF console interface.

**Key Features:**
- **Operation**: `sendOperatorCommand` (PUT `/restconsoles/consoles/defcn`)
- **Authentication**: Basic Auth with z/OS credentials
- **Common Commands Supported**:
  - `D A,L` - Display active address spaces
  - `D U,DASD` - Display DASD usage
  - `D IPLINFO` - Display IPL information
  - `D M=CPU` - Display CPU configuration
  - `F jobname,command` - Modify job commands

**Request Format:**
```json
{
  "cmd": "D IPLINFO"
}
```

**Response Format:**
```json
{
  "cmd-response": "C0000001",
  "cmd-response-key": "C0000001",
  "cmd-response-url": "/zosmf/restconsoles/consoles/defcn/solmsgs/C0000001",
  "sol-key-detected": "true"
}
```

**Security Requirements:**
- Valid z/OS user credentials
- Console command authority (RACF/SAF permissions)

### `tools/tsoCommand.yaml`

OpenAPI specification for z/OSMF TSO/E Address Space Services API.

**Purpose**: Allows the agent to execute TSO commands in a TSO address space.

**Key Features:**
- **Operation**: `executeTsoCommand` (PUT `/tsoApp/v1/tso`)
- **Authentication**: Basic Auth with z/OS credentials
- **Common Commands Supported**:
  - `TIME` - Display current time and date
  - `LISTDS` - List dataset information
  - `LISTCAT` - List catalog entries
  - `ALLOCATE` - Allocate datasets
  - `DELETE` - Delete datasets
  - `RENAME` - Rename datasets

**Request Format:**
```json
{
  "tsoCmd": "TIME"
}
```

**Response Format:**
```json
{
  "servletKey": "TSOSERVLET-127-aabccddeeff",
  "ver": "0100",
  "reused": true,
  "timeout": false,
  "sessionID": "0x37",
  "tsoData": [
    {
      "TSO MESSAGE": {
        "VERSION": "0100",
        "DATA": "TIME=13:45:32  DATE=2024/03/08"
      }
    }
  ],
  "appID": "IZUFPROC"
}
```

**Security Requirements:**
- Valid z/OS user credentials
- TSO segment defined in security system
- Commands execute with user's authority

## 🚀 Step-by-Step Setup Guide

### Prerequisites

Before creating the IPL-check custom agent, ensure you have:

1. **watsonx Orchestrate Environment**
   - Access to watsonx Orchestrate instance
   - Admin or developer permissions

2. **z/OS System Access**
   - z/OSMF server URL and port
   - Valid z/OS user credentials
   - Console command authority
   - TSO segment configured

3. **Required Information**
   - z/OSMF endpoint URL (e.g., `https://your-zosmf-server:10443/zosmf`)
   - z/OS username and password

### Step 1: Create z/OSMF Connection

The connection provides authentication and endpoint configuration for z/OSMF APIs.

1. **Navigate to Connections**
   - Log in to watsonx Orchestrate
   - Go to **Connections** section
   - Click **Create Connection**

2. **Configure Connection Details**
   - **Name**: `zosmf_connection`
   - **Type**: Select **Custom** or **REST API**
   - **Base URL**: Enter your z/OSMF URL (e.g., `https://itzvsi-zos-pqxlsmj.techzone.ibm.com:10443/zosmf`)

3. **Set Authentication**
   - **Auth Type**: Select **Basic Authentication**
   - **Username**: Enter your z/OS user ID
   - **Password**: Enter your z/OS password

4. **Test and Save**
   - Click **Test Connection** to verify connectivity
   - Click **Save** to create the connection

### Step 2: Import Operator Command Tool

This tool enables the agent to issue MVS operator commands.

1. **Navigate to Tools**
   - Go to **Tools** section in watsonx Orchestrate
   - Click **Import Tool** or **Add Tool**

2. **Upload Tool Definition**
   - Select **OpenAPI Specification**
   - Upload `tools/operatorCommand.yaml`
   - Or paste the YAML content directly

3. **Configure Tool**
   - **Tool Name**: `sendOperatorCommand`
   - **Connection**: Select `zosmf_connection` (created in Step 1)
   - **Operation**: Verify `sendOperatorCommand` is selected

4. **Map Parameters**
   - Ensure the `cmd` parameter is properly mapped
   - Verify authentication headers are configured

5. **Test the Tool**
   - Test with command: `D IPLINFO`
   - Verify successful response
   - Click **Save**

### Step 3: Import TSO Command Tool

This tool allows the agent to execute TSO commands.

1. **Navigate to Tools**
   - Go to **Tools** section
   - Click **Import Tool** or **Add Tool**

2. **Upload Tool Definition**
   - Select **OpenAPI Specification**
   - Upload `tools/tsoCommand.yaml`
   - Or paste the YAML content directly

3. **Configure Tool**
   - **Tool Name**: `executeTsoCommand`
   - **Connection**: Select `zosmf_connection` (same connection as Step 1)
   - **Operation**: Verify `executeTsoCommand` is selected

4. **Map Parameters**
   - Ensure the `tsoCmd` parameter is properly mapped
   - Verify request body structure

5. **Test the Tool**
   - Test with command: `TIME`
   - Verify response contains `"message": "READY "`
   - Click **Save**

### Step 4: Create the IPL-check Agent

Now create the agent that orchestrates the validation workflow.

1. **Navigate to Agents**
   - Go to **Agents** section in watsonx Orchestrate
   - Click **Create Agent** or **New Agent**

2. **Configure Basic Settings**
   - **Name**: `IPL_Validator`
   - **Description**: `Agent that runs through a series of checks to make sure systems are healthy after an IPL`
   - **Type**: Select **Native Agent**

3. **Set LLM Configuration**
   - **Model**: Select `watsonx/meta-llama/llama-3-3-70b-instruct`
   - **Style**: Select **React** (for reasoning and action)

4. **Add Instructions**
   
   Copy and paste the following instructions:
   
   ```
   You are going to run a series of commands using your tools to verify configurations after an IPL on a z/OS. You will follow the steps in order. You will print out to the user what number step you are running, what you high level action you will perform (ex- checking what IPL pack the system is on by running D IPLINFO), and the full output of the step in a pretty format.

   STEP 1. check to make sure you are on the right IPL pack. run your Issue an operator command from the system console tool using the command "D IPLINFO". Extract the value inside CURRENT IPL DEVICE from the response
   Print out the full output. Format the response prettily.

   Step 2. check to make sure TSO is running. run your Execute TSO command in an existing TSO address space tool using the default command TIME. If you get "message": "READY " in your response, TSO is running.
   Print out the full response. Format the full response prettily

   Step 3. Check that OMVS is running. run your Issue an operator command from the system console tool using the command "D OMVS".
   Print out the full response. Format the full response prettily

   Step 4. Make sure there are no mount failures on OMVS. run your Issue an operator command from the system console tool using the command "D OMVS,MF"
   Print out the full response. Format the full response prettily
   ```

5. **Add Tools to Agent**
   - Click **Add Tool**
   - Select `sendOperatorCommand` (from Step 2)
   - Click **Add Tool** again
   - Select `executeTsoCommand` (from Step 3)

6. **Configure Collaborators** (Optional)
   - Leave empty for standalone agent
   - Or add other agents if building a multi-agent system

7. **Save and Test**
   - Click **Save** to create the agent
   - Click **Test** to validate functionality

### Step 5: Test the Agent

Verify the agent performs IPL validation correctly.

1. **Start a Conversation**
   - Open the agent in the chat interface
   - Send a message: `Please validate the system after IPL`

2. **Expected Behavior**
   
   The agent should:
   
   **Step 1 Output:**
   ```
   Running Step 1: IPL Pack Verification
   High Level Action: Checking what IPL pack the system is on by running D IPLINFO
   Executing operator command: D IPLINFO
   
   Output:
   [IPL information including system name, IPL volume, date/time, etc.]
   CURRENT IPL DEVICE: [extracted device value]
   ```
   
   **Step 2 Output:**
   ```
   Running Step 2: TSO Status Check
   High Level Action: Verifying TSO is running by executing TIME command
   Executing TSO command: TIME
   
   Output:
   TIME=13:45:32  DATE=2024/03/08
   Status: TSO is running (READY message received)
   ```
   
   **Step 3 Output:**
   ```
   Running Step 3: OMVS Status Check
   High Level Action: Checking that OMVS is running by executing D OMVS
   Executing operator command: D OMVS
   
   Output:
   [OMVS status information including active processes, file systems, etc.]
   ```
   
   **Step 4 Output:**
   ```
   Running Step 4: OMVS Mount Verification
   High Level Action: Checking for mount failures in OMVS by executing D OMVS,MF
   Executing operator command: D OMVS,MF
   
   Output:
   [Mount failure information - should show no failures if system is healthy]
   ```

3. **Verify Results**
   - Confirm all four steps execute successfully in order
   - Check that output is formatted clearly and prettily
   - Verify CURRENT IPL DEVICE is extracted from Step 1
   - Confirm TSO READY message is detected in Step 2
   - Ensure OMVS status is displayed in Step 3
   - Verify mount failures (or lack thereof) are shown in Step 4
   - Ensure error handling works if commands fail

### Step 6: Deploy to Production (Optional)

Once testing is complete, deploy the agent for production use.

1. **Review Configuration**
   - Verify all connections are using production credentials
   - Ensure proper security permissions are in place
   - Review agent instructions for accuracy

2. **Set Access Controls**
   - Configure user/group permissions
   - Set up audit logging if required
   - Define usage policies

3. **Publish Agent**
   - Click **Publish** to make agent available
   - Add to relevant skill sets or workflows
   - Document usage for end users

4. **Monitor Performance**
   - Track agent invocations
   - Review success/failure rates
   - Collect user feedback

## 🔧 Customization Options

### Adding More Validation Steps

To extend the agent with additional checks:

1. **Update Agent Instructions**
   
   Add new steps to `agents/IPL-check.yaml`:
   ```yaml
   instructions: |
     ...existing steps...
     3. check VTAM status. run your operator command tool with "D NET,VTAM"
     4. verify JES2 is active. run your operator command tool with "D A,JES2"
   ```

2. **Add New Tools** (if needed)
   
   Create additional tool definitions for other z/OSMF APIs or external services.

3. **Update Tool List**
   
   Add new tools to the agent's `tools` section.

### Modifying Validation Logic

To change how the agent interprets results:

1. **Update Success Criteria**
   
   Modify the instructions to define different success conditions:
   ```yaml
   instructions: |
     2. check to make sure TSO is running. run your Execute TSO command tool using TIME.
        If the response contains "READY" and no error codes, TSO is healthy.
        If you see error messages, report them to the user and mark TSO as unhealthy.
   ```

2. **Add Error Handling**
   
   Include specific error scenarios:
   ```yaml
   instructions: |
     If any step fails:
     - Report the specific error message
     - Suggest remediation steps
     - Continue with remaining checks if possible
   ```

### Changing the LLM Model

To use a different language model:

1. Edit `agents/IPL-check.yaml`:
   ```yaml
   llm: ibm/granite-3-3-8b-instruct
   ```

2. Available models may include:
   - `meta-llama/llama-3-3-70b-instruct` (current)
   - `ibm/granite-3-3-8b-instruct`


## 🔍 Troubleshooting

### Connection Issues

**Problem**: Agent cannot connect to z/OSMF

**Solutions**:
- Verify z/OSMF URL is correct and accessible
- Check firewall rules allow HTTPS traffic
- Confirm z/OSMF service is running
- Test connection manually using curl or Postman

### Authentication Failures

**Problem**: 401 Unauthorized or 403 Forbidden errors

**Solutions**:
- Verify z/OS credentials are correct
- Check user has console command authority
- Ensure TSO segment is defined for the user
- Review RACF/SAF permissions

### Command Execution Errors

**Problem**: Commands fail or return unexpected results

**Solutions**:
- Test commands manually in z/OS console
- Verify command syntax is correct
- Check system resources are available
- Review z/OSMF logs for detailed errors

### Agent Not Following Instructions

**Problem**: Agent skips steps or produces incorrect output

**Solutions**:
- Review agent instructions for clarity
- Ensure tools are properly configured
- Test each tool independently
- Try a different LLM model
- Add more explicit step-by-step guidance

## 📚 Additional Resources

### z/OSMF Documentation
- [z/OSMF REST Services](https://www.ibm.com/docs/en/zos/2.5.0?topic=services-zosmf-rest-services)
- [Console Services API](https://www.ibm.com/docs/en/zos/2.5.0?topic=services-console-rest-services)
- [TSO/E Services API](https://www.ibm.com/docs/en/zos/2.5.0?topic=services-tsoe-address-space-services)

### watsonx Orchestrate
- [Agent Development Guide](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Custom Tool Integration](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [OpenAPI Specification](https://swagger.io/specification/)

### z/OS Commands
- [MVS System Commands](https://www.ibm.com/docs/en/zos/2.5.0?topic=commands-mvs-system)
- [TSO/E Commands](https://www.ibm.com/docs/en/zos/2.5.0?topic=commands-tsoe)

## 🤝 Contributing

To enhance this agent:

1. Fork or copy the directory structure
2. Make modifications to YAML files
3. Test thoroughly in a development environment
4. Document changes in this README
5. Share improvements with your team

## 📝 License

This custom agent implementation is provided as-is for use with watsonx Orchestrate and z/OS systems.

## ✨ Credits

Created with Bob - AI Software Engineering Assistant

---

**Last Updated**: March 2026  
**Version**: 1.0.0  
**Compatibility**: watsonx Orchestrate, z/OSMF 2.5+