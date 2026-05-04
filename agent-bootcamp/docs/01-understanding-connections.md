# Understanding Connections

Now that you have your environments and your ADK set up, now it's time to understand what is needed to create an agent for watsonx Assistant for Z.


This guide will provide step by step information on how to create connections to your z/OSMF backend and how they provide authentication and configuration for your tools.

## 📋 Overview

Connections are the "credentials and configuration" that allow your tools to communicate with external systems. They provide:
- Authentication (username/password, API keys, tokens)
- Server URLs and endpoints
- Environment-specific settings (draft vs. live)

**Connections in custom-agent2:**
- `zosmf_connection.yaml` - Connects to z/OSMF for operator and TSO commands

---

## 🔐 z/OSMF connection

### Purpose

This connection provides authentication and endpoint configuration for z/OSMF REST APIsthat will be used by the IPL-check agent.

### What It Connects To

- z/OSMF Console Services API (for operator commands)
- z/OSMF TSO Services API (for TSO commands)

### Creating the file
1. Create a folder or directory where you will store files for this bootcamp. From your Terminal or Command-Line, enter the following commands:
    ```
    mkdir agent-bootcamp
    cd agent-bootcamp
    ```
2. create a file called zosmf_connection.yaml
    ```
    touch zosmf_connection.yaml
    ```
3. open zosmf_connection.yaml for editing
    ```
    open zosmf_connection.yaml
    ```
### File Structure Breakdown
Copy and paste the following code in zosmf_connection.yaml
```yaml
spec_version: v1
kind: connection
app_id: zosmf
```

**Field explanations:**

| Field | Purpose | Value |
|-------|---------|-------|
| `spec_version` | Connection spec version | `v1` (current version) |
| `kind` | Type of configuration | `connection` (always this for connections) |
| `app_id` | Unique identifier for this connection | `zosmf` (must be unique) |

**Important:** The `app_id` is how tools reference this connection. It is important that the app_id reflects the endpoint the agent connects to. In this case, the ``app_id`` is `zosmf` because the agent needs to connect to zOSMF REST API endpoint. Another example of an `app_id` would be `ansible` if you have an agent that runs Ansible playbooks and therefore needs to connect to Ansible Automation Platform to run.<br> <br>


---
Next, copy and paste the following code to the bottom of your zosmf_connection.yaml
```yaml
environments:
    draft:
        kind: basic
        type: team
        server_url: <zosmf url>
```

**What is an environment?**

Environments allow different configurations for different stages:
- **draft**: Used during development and testing of your agent
- **live**: Used in production after publishing your agent so all team members can see and use it.

**Field explanations:**

| Field | Purpose | Value in draft |
|-------|---------|----------------|
| `kind` | Authentication type | `basic` (username/password) |
| `type` | Credential scope | `team` (shared by team) or `member` (per user) |
| `server_url` | Base URL for API calls | Your z/OSMF server URL |

**How to find your server URL:**
Your IBM representative for the bootcamp will give you the url. 
---

### Live Environment
Add the follow code to the end of zosmf_connection.yaml
```yaml
    live:
        kind: basic
        type: member
        server_url: https://<server url>:10443/zosmf/
```

**Differences from draft:**

| Setting | Draft | Live | Why Different? |
|---------|-------|------|----------------|
| `type` | `team` | `member` | Production uses individual credentials for audit trail |
| `server_url` | Test server | Production server | Different environments |

**Common pattern:**
- **Draft**: Team credentials, test server, relaxed settings
- **Live**: Member credentials, production server, strict settings


At a high level, this connection will allow your agent to connect to your zosmf endpoint using basic username and password authentication while it is live (published for official use in your organization). This username and password will be by member, meaning each indivudal using the agent will need to use their own credentials.  
If you'd like to learn more about other options you can choose for each of these fields, head to the `Dive Deeper` section. 

---

### Complete zosmf_connection.yaml Explained

```yaml
# Specification version - always v1
spec_version: v1

# This is a connection configuration
kind: connection

# Unique identifier - tools reference this connection by app_id
app_id: zosmf

# Environment-specific configurations
environments:
    # Development/testing environment
    draft:
        # Authentication method: username/password
        kind: basic
        
        # Credential scope: shared team credentials
        type: team
        
        # z/OSMF server URL (test environment)
        server_url: https://<server-url:10443/zosmf/
        
        # TLS version for secure communication
        ssl_protocol: TLSv1.2
    
    # Production environment
    live:
        # Authentication method: username/password
        kind: basic
        
        # Credential scope: individual user credentials
        type: member
        
        # z/OSMF server URL (production environment)
        server_url: https://<server url>:10443/zosmf/
        
        # TLS version for secure communication
        ssl_protocol: TLSv1.2
```

---

## Upload connection to Orchestrate
You have all the code you need to make this connection! Now all that's left is to upload it to Orchestrate. To do that, run the following command:
```
 orchestrate connections import --file connections/zosmf_connection.yaml
```
Your connection is now uploaded to Orchestrate! Now you just need to pass in the usernmae and password (since we are using basic authentication). To do this, run the following command (**replace < zosmf-password > with the password provided to you by your IBM rep**):

```
orchestrate connections set-credentials --app-id zosmf --env draft --username admin --password < zosmf-password >
```

Optional- you can run ``orchestrate connections list`` to verify if your connection is live.

Done! You can proceed on to the next section or continue reading this page to learn more information about connection security options and get a sneak peak at how tools and agents integrate with connections.
- [Creating Tools](./02-understanding-tools.md) - Creating tools for your agent

---

## Dive Deeper
### Other Options You Can Choose in Your Connection Environment Fields
| Field | Purpose | Value in draft |
|-------|---------|----------------|
| `kind` | Authentication type | `basic` (username/password) |
| `type` | Credential scope | `team` (shared by team) or `member` (per user) |
| `server_url` | Base URL for API calls | Your z/OSMF server URL |
#### Authentication Type: `kind: basic`

**What it means:** Uses HTTP Basic Authentication (username and password).

**How it works:**
1. User provides z/OS username and password
2. watsonx Orchestrate encodes them as Base64
3. Adds `Authorization: Basic <encoded-credentials>` header to API requests

**When to use:**
- z/OSMF with basic authentication enabled
- Simple username/password authentication
- Most common for z/OS systems

**Alternatives:**
```yaml
kind: oauth2      # OAuth 2.0 authentication
kind: apikey      # API key authentication
kind: bearer      # Bearer token authentication
```

---

#### Credential Scope: `type: team`

**What it means:** Credentials are shared across the team.

**How it works:**
- One set of credentials configured for the entire team
- All team members use the same z/OS user ID
- Useful for shared service accounts

**Alternative: `type: member`**
```yaml
type: member  # Each user provides their own credentials
```

**When to use each:**

| Type | Use When | Pros | Cons |
|------|----------|------|------|
| `team` | Using a service account | Simple setup, one credential | Less audit trail, shared permissions |
| `member` | Each user has own z/OS ID | Better audit trail, individual permissions | Each user must configure credentials |

----

## #How Connections Link to Tools

#### In the Tool File

Tools don't directly reference connections. Instead, they have their own server definitions in their yamls:
```yaml
# operatorCommand.yaml
servers:
  - url: https://<server url>>:10443/zosmf
```

#### Connection Mapping

The mapping of connection to tool comes when uploading with ADK. You map tools to connections by running the following command in your cli (we will get to this in the Creating Tools section of this bootcamp):
```bash
# During upload, you specify which connection to use
orchestrate tool import operatorCommand.yaml -a zosmf
```

#### Runtime Flow

1. **Agent calls tool:** `sendOperatorCommand`
2. **Tool needs authentication:** Looks up connection
3. **Connection provides:** Credentials + server URL
4. **API call made:** With proper authentication

```
Agent → Tool → Connection → z/OSMF API
        ↓      ↓
        operatorCommand.yaml → zosmf_connection.yaml
```

---

### Common Connection Patterns

### Pattern 1: Basic Authentication (Username/Password)

**Used by:** zosmf_connection

```yaml
kind: basic
type: team  # or member
server_url: https://server.com/api
```

**When to use:**
- Traditional username/password systems
- z/OS, z/OSMF, many enterprise APIs
- Simple authentication requirements

---

### Pattern 2: OAuth 2.0 Authentication

**Example (not used in this bootcamp):**

```yaml
kind: oauth2
type: member
server_url: https://api.example.com
oauth:
  token_url: https://auth.example.com/oauth/token
  client_id: your-client-id
  scopes:
    - read
    - write
```

**When to use:**
- APIs requiring token-based auth
- Services with OAuth 2.0 support

---

### Pattern 3: API Key Authentication

**Example (not used in this bootcamp):**

```yaml
kind: apikey
type: team
server_url: https://api.example.com
apikey:
  header_name: X-API-Key
  key_location: header  # or query
```

**When to use:**
- APIs that use API keys
- Simple token-based authentication
- Services without OAuth support

---

### Pattern 4: Bearer Token Authentication

**Example (not in IPL-check):**

```yaml
kind: bearer
type: member
server_url: https://api.example.com
bearer:
  token_url: https://auth.example.com/token
```

**When to use:**
- JWT-based authentication
- Token-based APIs
- Modern microservices


---

## 🔗 How Everything Connects

```
┌─────────────────┐
│  IPL-check      │
│  Agent          │
└────────┬────────┘
         │ uses tools
         ↓
┌─────────────────┐     ┌─────────────────┐
│ sendOperator    │     │ executeTso      │
│ Command         │     │ Command         │
│ (tool)          │     │ (tool)          │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │ both use connection
                     ↓
         ┌─────────────────────┐
         │ zosmf_connection    │
         │ - Credentials       │
         │ - Server URL        │
         │ - SSL config        │
         └──────────┬──────────┘
                    │
                    ↓
         ┌─────────────────────┐
         │ z/OSMF REST APIs    │
         │ - Console API       │
         │ - TSO API           │
         └─────────────────────┘
```

---

## 📚 Next Steps

- [Creating Tools](./02-understanding-tools.md) - Creating tools for your agent

---