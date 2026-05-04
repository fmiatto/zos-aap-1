# Understanding Tools (OpenAPI Specifications)

Tools are the "hands" of your agent - they allow the agent to interact with external systems through REST APIs, python scripts, or agentic workflows. Tools are defined using:
  - OpenAPI specifications that describe how to call these APIs.
  - python scripts that perform some actions
  - agentic workflows that utilize the watsonx Orchestrate UI to drag and drop agents, tools, and queries into a workflow.

The agent you are creating requires two tools: one that runs MVS operator commands and one that runs TSO commands. The tools that you will create in this section of the guide are z/OSMF OpenAPI specs that describe how to call these APIs.

## What is an OpenAPI Specification?

An OpenAPI spec is a standard format for describing REST APIs. While each REST API is different, all OpenAPI specs require the same general information:

### Required Components

1. **Server URL** - Where the API is hosted
2. **Operation ID** - Unique name for the operation (used in agent's tools list)
3. **Description** - What the API does (helps the LLM understand when to use it)
4. **At least one response** - What the API returns

### Optional Components

- **Parameters** - Variables that can be passed to the API (like commands to execute)
- **Request body** - Data sent with the request
- **Authentication** - How to authenticate (Basic Auth, API keys, etc.)
- **Multiple responses** - Different response codes (200, 400, 401, 500, etc.)

## 📄 Tool 1: operatorCommand.yaml

Now let's put these abstract concepts into practice. We are going to create a tool that  allows agents to issue MVS operator commands via z/OSMF Console API. First, we must make the file. In your terminal or Command-Line, please enter the following commands:
```
touch operatorCommand.yaml
open operatorCommand.yaml
```
You should see an empty file now opened in your default text editor.

### Complete Code
Please copy and paste the following code into the file:

```yaml
openapi: 3.0.0
info:
  description: z/OSMF REST Console Services API for issuing operator commands
  title: z/OSMF Console Command API
  version: 1.0.0
  x-ibm-grounded-description: false
  x-csrf-zosmf-header: true
servers:
- url: https://<server-url>:10443/zosmf
paths:
  /restconsoles/consoles/defcn:
    put:
      operationId: sendOperatorCommand
      summary: Issue an operator command from the system console
      description: |
        Issues an MVS operator command through the z/OSMF REST console services.
        The command is executed on the default console (defcn) and returns the command response.
        
        **Key Features:**
        - Execute any MVS operator command
        - Receive synchronous command responses
        - Get message IDs and text from command output
        - Support for solicited and unsolicited messages
        
        **Common Commands:**
        - D A,L - Display active address spaces
        - D U,DASD - Display DASD usage
        - D IPLINFO - Display IPL information
        - D M=CPU - Display CPU configuration
        - F jobname,command - Modify job command
        
        **Security:**
        - Requires valid z/OS credentials with console authority
        - User must have appropriate RACF/SAF permissions for console commands
      security:
        - BasicAuth: []
      parameters:
        - name: X-CSFR-ZOSMF-HEADER
          in: header
          description: CSRF protection header for z/OSMF
          required: false
          schema:
            type: boolean
            default: true
      requestBody:
        description: The operator command to execute
        required: true
        x-ibm-body-name: command_request
        content:
          application/json:
            schema:
              type: object
              required:
                - cmd
              properties:
                cmd:
                  type: string
                  description: |
                    The MVS operator command to execute.
                    Can be any valid MVS system command.
                  example: "D A,L"
            examples:
              displayActive:
                summary: Display active address spaces
                value:
                  cmd: "D A,L"
              displayDasd:
                summary: Display DASD usage
                value:
                  cmd: "D U,DASD"
              iplInfo:
                summary: Display IPL information
                value:
                  cmd: "D IPLINFO"
      responses:
        '200':
          description: Command executed successfully
          content:
            application/json:
              schema:
                type: object
                required:
                  - cmd-response
                properties:
                  cmd-response:
                    type: string
                    description: |
                      The solicited message key for this command response.
                      Used to retrieve additional messages if needed.
                    example: "C0000001"
                  cmd-response-key:
                    type: string
                    description: The command response key
                    example: "C0000001"
                  cmd-response-url:
                    type: string
                    description: URL to retrieve additional command responses
                    example: "/zosmf/restconsoles/consoles/defcn/solmsgs/C0000001"
                  cmd-response-uri:
                    type: string
                    description: URI for the command response
                    example: "/zosmf/restconsoles/consoles/defcn/solmsgs/C0000001"
                  sol-key-detected:
                    type: string
                    description: |
                      Indicates if a solicited message key was detected in the response.
                      Values: "true" or "false"
                    example: "true"
              examples:
                displayActiveResponse:
                  summary: Response from D A,L command
                  value:
                    cmd-response: "C0000001"
                    cmd-response-key: "C0000001"
                    cmd-response-url: "/zosmf/restconsoles/consoles/defcn/solmsgs/C0000001"
                    cmd-response-uri: "/zosmf/restconsoles/consoles/defcn/solmsgs/C0000001"
                    sol-key-detected: "true"
                
                iplInfoResponse:
                  summary: Response from D IPLINFO command
                  value:
                    cmd-response: "C0000002"
                    cmd-response-key: "C0000002"
                    cmd-response-url: "/zosmf/restconsoles/consoles/defcn/solmsgs/C0000002"
                    sol-key-detected: "true"
        
        '400':
          description: Bad Request - Invalid command or parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                invalidCommand:
                  summary: Invalid command syntax
                  value:
                    category: 1
                    rc: 4
                    reason: 0
                    message: "Invalid command syntax"
                    details:
                      - "The command could not be parsed"
                      - "Check command syntax and try again"
                
                missingParameter:
                  summary: Missing required parameter
                  value:
                    category: 1
                    rc: 4
                    reason: 0
                    message: "Missing required parameter 'cmd'"
                    details:
                      - "The 'cmd' parameter is required"
        
        '401':
          description: Unauthorized - Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                message: "Authentication required"
                details:
                  - "Valid z/OS credentials must be provided"
        
        '403':
          description: Forbidden - Insufficient console authority
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                category: 1
                rc: 8
                reason: 913
                message: "Access denied"
                details:
                  - "User does not have console command authority"
                  - "Contact your security administrator for CONSOLE access"
        
        '500':
          description: Internal Server Error - z/OSMF or z/OS system error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                systemError:
                  summary: System error during command execution
                  value:
                    category: 8
                    rc: 16
                    reason: 0
                    message: "System error occurred"
                    details:
                      - "Unable to execute command on z/OS system"
                      - "Check z/OSMF logs for details"
                
                consoleUnavailable:
                  summary: Console not available
                  value:
                    category: 8
                    rc: 12
                    reason: 0
                    message: "Console unavailable"
                    details:
                      - "The default console (defcn) is not available"
                      - "Try again later or contact system administrator"

components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
      description: |
        Basic authentication using z/OS user ID and password.
        User must have console command authority.
  
  schemas:
    Error:
      type: object
      description: Error response object returned by z/OSMF
      required:
        - message
      properties:
        category:
          type: integer
          description: |
            Error category code:
            - 0: Success with warnings
            - 1: Client error (4xx)
            - 4: Resource not found
            - 8: Server/system error (5xx)
          example: 1
        
        rc:
          type: integer
          description: |
            Return code from z/OS or z/OSMF.
            Higher values indicate more severe errors.
          example: 8
        
        reason:
          type: integer
          description: |
            Reason code providing additional error context.
            Interpretation depends on the rc value.
          example: 0
        
        message:
          type: string
          description: Human-readable error message
          example: "Command execution failed"
        
        details:
          type: array
          items:
            type: string
          description: Additional error details and suggestions
          example:
            - "The command could not be executed"
            - "Check command syntax and permissions"
        
        stack:
          type: string
          description: Stack trace (only included in debug mode)
          example: "Error at line 123..."
```

### Key Elements Explained

**Server URL**: `https://<server-url>:10443/zosmf`
- Base URL for all API calls -> replace this with the z/OSMF url that your IBM respresentative provides.

**Operation ID**: `sendOperatorCommand`
- **CRITICAL**: This name must match exactly in the agent's tools list (which you will create in the next section of this guide)
- This is how the agent references this tool

**Request Body with Variable**: The `cmd` parameter
- Allows users to pass in the specific command to run
- Example: `{"cmd": "D IPLINFO"}`
- The agent can dynamically set this value based on instructions

**Responses**: Multiple response codes (200, 400, 401, 403, 500)
- Defines what the API returns in different scenarios
- Helps the LLM understand success and error conditions

**Authentication**: BasicAuth
- Credentials come from the connection file
- watsonx Orchestrate automatically adds them to requests


## Tool 2: tsoCommand.yaml

Now, time for the second tool your agent will have access to. This tool allows agents to execute TSO commands via z/OSMF TSO/E Address Space Services API. This API is used to execute TSO commands on z/OS. Please execute the following commands in your Terminal or Command-Line:
```
touch tsoCommand.yaml
open tsoCommand.yaml
```

### Complete Code
Now copy and paste the following code into tsoCommand.yaml:
```yaml
openapi: 3.0.0
info:
  description: z/OSMF TSO/E Address Space Services API for executing TSO commands
  title: z/OSMF TSO Command API
  version: 1.0.0
  contact:
    name: IBM z/OSMF Documentation
    url: https://www.ibm.com/docs/en/zos/2.5.0?topic=services-tsoe-address-space-services
  x-ibm-grounded-description: false
  x-csrf-zosmf-header: true

servers:
  - url: https://<server-url>:10443/zosmf
    description: z/OSMF server endpoint

paths:
  /tsoApp/v1/tso:
    put:
      operationId: executeTsoCommand
      summary: Execute a TSO command in an existing TSO address space
      description: |
        Executes a TSO/E command in an existing TSO address space via z/OSMF.
        The command is sent to the TSO session identified by the servlet key.
        
        **Common TSO Commands:**
        - TIME - Display current time and date
        - LISTDS - List dataset information
        - LISTCAT - List catalog entries
        - ALLOCATE - Allocate datasets
        - DELETE - Delete datasets
        - RENAME - Rename datasets
        - SEND - Send messages to users
        - PROFILE - Display or modify TSO profile
        
        **Workflow:**
        1. First, create a TSO address space (POST /restfiles/tso/start)
        2. Execute commands using this endpoint (PUT /restfiles/tso/{servletKey})
        3. Retrieve command output (GET /restfiles/tso/{servletKey})
        4. End the TSO session (DELETE /restfiles/tso/{servletKey})
        
        **Security:**
        - Requires valid z/OS credentials
        - User must have TSO segment defined in security system
        - Commands execute with user's authority
      
      security:
        - BasicAuth: []
      
      requestBody:
        description: The TSO command to execute
        required: true
        x-ibm-body-name: tso_command
        content:
          application/json:
            schema:
              type: object
              required:
                - tsoCmd
              properties:
                tsoCmd:
                  type: string
                  description: |
                    The TSO command to execute.
                    Can be any valid TSO system command.
            examples:
              timeCommand:
                summary: Execute TIME command
                value:
                  tsoCmd: "TIME"
      
      responses:
        '200':
          description: Command executed successfully
          content:
            application/json:
              schema:
                type: object
                required:
                  - servletKey
                  - ver
                  - reused
                  - timeout
                properties:
                  servletKey:
                    type: string
                    description: The servlet key for this TSO session
                    example: "TSOSERVLET-127-aabccddeeff"
                  
                  ver:
                    type: string
                    description: API version
                    example: "0100"
                  
                  reused:
                    type: boolean
                    description: Indicates if the TSO session was reused
                    example: true
                  
                  timeout:
                    type: boolean
                    description: Indicates if a timeout occurred
                    example: false
                  
                  sessionID:
                    type: string
                    description: The TSO session ID
                    example: "0x37"
                  
                  tsoData:
                    type: array
                    description: Array of TSO response data
                    items:
                      type: object
                      properties:
                        TSO MESSAGE:
                          type: object
                          properties:
                            VERSION:
                              type: string
                              example: "0100"
                            DATA:
                              type: string
                              description: The command output or message
                              example: "TIME=13:45:32  DATE=2024/03/08"
                  
                  appID:
                    type: string
                    description: Application ID
                    example: "IZUFPROC"
              
              examples:
                timeCommandResponse:
                  summary: Response from TIME command
                  value:
                    servletKey: "TSOSERVLET-127-aabccddeeff"
                    ver: "0100"
                    reused: true
                    timeout: false
                    sessionID: "0x37"
                    tsoData:
                      - TSO MESSAGE:
                          VERSION: "0100"
                          DATA: "TIME=13:45:32  DATE=2024/03/08"
                      - TSO PROMPT:
                          VERSION: "0100"
                          HIDDEN: "false"
                    appID: "IZUFPROC"
                
                listdsResponse:
                  summary: Response from LISTDS command
                  value:
                    servletKey: "TSOSERVLET-127-aabccddeeff"
                    ver: "0100"
                    reused: true
                    timeout: false
                    tsoData:
                      - TSO MESSAGE:
                          VERSION: "0100"
                          DATA: "USER.TEST.DATA"
                      - TSO MESSAGE:
                          VERSION: "0100"
                          DATA: "--RECFM-LRECL-BLKSIZE-DSORG"
                      - TSO MESSAGE:
                          VERSION: "0100"
                          DATA: "  FB    80    3120   PS"
        
        '400':
          description: Bad Request - Invalid command or parameters
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                invalidCommand:
                  summary: Invalid TSO command
                  value:
                    category: 1
                    rc: 4
                    reason: 0
                    message: "Invalid TSO command"
                    details:
                      - "The command syntax is incorrect"
                      - "Check TSO command reference"
                
                missingData:
                  summary: Missing DATA field
                  value:
                    category: 1
                    rc: 4
                    reason: 0
                    message: "Missing required field 'DATA'"
                    details:
                      - "The DATA field in TSO RESPONSE is required"
        
        '401':
          description: Unauthorized - Authentication required
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                message: "Authentication required"
                details:
                  - "Valid z/OS credentials must be provided"
        
        '403':
          description: Forbidden - Insufficient permissions
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                category: 1
                rc: 8
                reason: 913
                message: "Access denied"
                details:
                  - "User does not have TSO authority"
                  - "Contact your security administrator"
        
        '404':
          description: TSO session not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                category: 4
                rc: 8
                reason: 0
                message: "TSO session not found"
                details:
                  - "The specified servlet key does not exist"
                  - "The TSO session may have timed out"
                  - "Create a new TSO session with POST /restfiles/tso/start"
        
        '500':
          description: Internal Server Error - z/OSMF or z/OS system error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                systemError:
                  summary: System error during command execution
                  value:
                    category: 8
                    rc: 16
                    reason: 0
                    message: "System error occurred"
                    details:
                      - "Unable to execute TSO command"
                      - "Check z/OSMF logs for details"
                
                tsoTimeout:
                  summary: TSO session timeout
                  value:
                    category: 8
                    rc: 12
                    reason: 0
                    message: "TSO session timeout"
                    details:
                      - "The TSO session has timed out"
                      - "Create a new session and retry"

components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
      description: |
        Basic authentication using z/OS user ID and password.
        User must have a TSO segment defined in the security system.
  
  schemas:
    Error:
      type: object
      description: Error response object returned by z/OSMF
      required:
        - message
      properties:
        category:
          type: integer
          description: |
            Error category code:
            - 0: Success with warnings
            - 1: Client error (4xx)
            - 4: Resource not found
            - 8: Server/system error (5xx)
          example: 1
        
        rc:
          type: integer
          description: |
            Return code from z/OS or z/OSMF.
            Higher values indicate more severe errors.
          example: 8
        
        reason:
          type: integer
          description: |
            Reason code providing additional error context.
            Interpretation depends on the rc value.
          example: 0
        
        message:
          type: string
          description: Human-readable error message
          example: "TSO command execution failed"
        
        details:
          type: array
          items:
            type: string
          description: Additional error details and suggestions
          example:
            - "The TSO command could not be executed"
            - "Check command syntax and permissions"
        
        stack:
          type: string
          description: Stack trace (only included in debug mode)
          example: "Error at line 123..."
```

### Key Differences from operatorCommand.yaml

| Aspect | operatorCommand.yaml | tsoCommand.yaml |
|--------|---------------------|-----------------|
| **Purpose** | MVS operator commands | TSO user commands |
| **Endpoint** | `/restconsoles/consoles/defcn` | `/tsoApp/v1/tso` |
| **Operation ID** | `sendOperatorCommand` | `executeTsoCommand` |
| **Request Field** | `cmd` | `tsoCmd` |
| **Session** | No session needed | Uses TSO session |
| **Authority** | Console authority | TSO segment required |

---
## Uploading your Tool to watsonx Assistant for Z
In your Terminal or Command Line, run the following commands:
```
orchestrate tools import -k openapi -f operatorCommand.yaml -a zosmf
orchestrate tools import -k openapi -f tsoCommand.yaml -a zosmf
```
These commands upload these two tools to watsonx Orchestrate and associates them with the zosmf connection you created in the previous section. When your agent runs its tools, it will use the authentication defined in the zosmf connection. 

## 📚 Next Steps

- [Create Your Agent](./03-understanding-agent-fields.md) - Creating your Post-IPL Validator agent]

---

## Optional- Dive Deeper
### How Agents Use Tools
When creating an agent, you will define what tools are available to them. The agent will then be able to use these tools in its instructions.
#### Example- In the Agent File (we will get to this in the next section) 
```yaml
# agents/IPL-check.yaml
tools: 
  - sendOperatorCommand    # Must match operationId in tool file
  - executeTsoCommand      # Must match operationId in tool file
```

#### Example Execution Flow

1. **Agent reads instructions**: "Run command D IPLINFO using sendOperatorCommand tool"
2. **Agent identifies tool**: Looks up `sendOperatorCommand` in its tools list
3. **Agent constructs request**: Creates JSON with the command: `{"cmd": "D IPLINFO"}`
4. **watsonx Assistant for Z makes API call**: Sends request to z/OSMF with credentials
5. **API returns response**: Command output comes back
6. **Agent processes response**: Extracts information and formats for user

### Creating Your Own Tools

#### Basic Template

```yaml
openapi: 3.0.0
info:
  title: My Tool Name
  description: What this tool does
  version: 1.0.0
servers:
  - url: https://your-api-server.com
paths:
  /your/api/endpoint:
    post:  # or get, put, delete
      operationId: myToolName  # IMPORTANT: Use this in agent's tools list
      summary: Short description
      description: Detailed description for the LLM
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                parameterName:  # Variables users can pass in
                  type: string
                  description: What this parameter does
      responses:
        '200':
          description: Success response
          content:
            application/json:
              schema:
                type: object
                properties:
                  result:
                    type: string
```

#### Tips for Tool Creation

1. **Choose a clear operationId** - This is how agents reference your tool
2. **Write good descriptions** - The LLM uses these to decide when to use the tool
3. **Define parameters clearly** - Make it obvious what variables can be passed in
4. **Include examples** - Show sample requests and responses
5. **Document all responses** - Include success and error scenarios

---