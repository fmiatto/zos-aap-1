# IPL-check Agent Documentation

Complete guide for understanding and deploying the IPL-check custom agent to watsonx Orchestrate.

## 📚 Documentation Overview

This documentation is organized into four comprehensive guides that take you from understanding the basics to deploying your agent in production.

### [01 - Understanding Agent Fields](./01-understanding-agent-fields.md)
**What you'll learn:**
- Every field in the `IPL-check.yaml` agent file
- What each field does and why it matters
- How to modify the agent configuration
- Best practices for agent design

**Start here if:** You're new to watsonx Orchestrate agents or want to understand how the IPL-check agent works.

**Key topics:**
- Agent specification structure
- Instructions and workflow design
- LLM selection and reasoning styles
- Tool integration
- Collaborator patterns

---

### [02 - Understanding Tools](./02-understanding-tools.md)
**What you'll learn:**
- How OpenAPI specifications define tools
- What the operator command tool does
- What the TSO command tool does
- How tools connect to agents

**Start here if:** You want to understand how the agent interacts with z/OSMF APIs or need to create new tools.

**Key topics:**
- OpenAPI specification structure
- Request and response formats
- Authentication requirements
- Tool-to-agent mapping
- Creating custom tools

---

### [03 - Understanding Connections](./03-understanding-connections.md)
**What you'll learn:**
- How connections provide authentication
- Environment-specific configurations (draft vs. live)
- Credential management (team vs. member)
- SSL/TLS configuration

**Start here if:** You need to configure authentication or connect to different z/OSMF servers.

**Key topics:**
- Connection types (basic, OAuth, API key)
- Credential scopes
- Server URL configuration
- Security settings
- Multi-environment setup

---

### [04 - Uploading with ADK](./04-uploading-with-adk.md)
**What you'll learn:**
- Step-by-step deployment process
- ADK command reference
- Testing and validation
- Publishing to production
- Troubleshooting common issues

**Start here if:** You're ready to deploy the agent to watsonx Orchestrate.

**Key topics:**
- ADK installation and configuration
- Upload order (connections → tools → agents)
- Testing workflows
- Version management
- Production deployment

---

## 🚀 Quick Start Guide

### For Complete Beginners

1. **Read the guides in order:**
   - Start with [Understanding Agent Fields](./01-understanding-agent-fields.md)
   - Then [Understanding Tools](./02-understanding-tools.md)
   - Then [Understanding Connections](./03-understanding-connections.md)
   - Finally [Uploading with ADK](./04-uploading-with-adk.md)

2. **Follow the deployment steps:**
   - Install ADK
   - Upload connections
   - Upload tools
   - Upload agent
   - Test and publish

### For Experienced Users

**Just want to deploy?** Jump to [Uploading with ADK](./04-uploading-with-adk.md) and follow the complete workflow.

**Need to modify the agent?** See [Understanding Agent Fields](./01-understanding-agent-fields.md) for configuration options.

**Creating new tools?** Check [Understanding Tools](./02-understanding-tools.md) for OpenAPI patterns.

**Connection issues?** Refer to [Understanding Connections](./03-understanding-connections.md) for troubleshooting.

---

## 📁 File Structure Reference

```
custom-agent2/
├── agents/
│   └── IPL-check.yaml              # Agent configuration
├── tools/
│   ├── operatorCommand.yaml        # MVS operator command tool
│   └── tsoCommand.yaml             # TSO command tool
├── connections/
│   ├── zosmf_connection.yaml       # z/OSMF authentication
│   └── ansible_connection.yaml     # Ansible authentication (example)
├── docs/
│   ├── README.md                   # This file
│   ├── 01-understanding-agent-fields.md
│   ├── 02-understanding-tools.md
│   ├── 03-understanding-connections.md
│   └── 04-uploading-with-adk.md
└── README.md                       # Project overview
```

---

## 🎯 Common Tasks

### Task: Add a New Validation Step

1. **Modify agent instructions** ([Guide 01](./01-understanding-agent-fields.md))
   ```yaml
   # agents/IPL-check.yaml
   instructions: |
     ...existing steps...
     Step 5. Check JES2 status. run your Issue an operator command...
   ```

2. **Test the change** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk agent upload agents/IPL-check.yaml --update
   adk agent test IPL_Validator
   ```

3. **Publish** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk agent publish IPL_Validator
   ```

---

### Task: Create a New Tool

1. **Create OpenAPI spec** ([Guide 02](./02-understanding-tools.md))
   ```yaml
   # tools/newTool.yaml
   openapi: 3.0.0
   paths:
     /api/endpoint:
       post:
         operationId: myNewTool
   ```

2. **Upload tool** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk tool upload tools/newTool.yaml --connection zosmf
   ```

3. **Add to agent** ([Guide 01](./01-understanding-agent-fields.md))
   ```yaml
   # agents/IPL-check.yaml
   tools:
     - sendOperatorCommand
     - executeTsoCommand
     - myNewTool
   ```

---

### Task: Change z/OSMF Server

1. **Update connection** ([Guide 03](./03-understanding-connections.md))
   ```yaml
   # connections/zosmf_connection.yaml
   environments:
     draft:
       server_url: https://new-server.com:10443/zosmf/
   ```

2. **Upload updated connection** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk connection upload connections/zosmf_connection.yaml --update
   ```

3. **Test tools and agent** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk tool test sendOperatorCommand
   adk agent test IPL_Validator
   ```

---

### Task: Switch from Team to Member Credentials

1. **Update connection** ([Guide 03](./03-understanding-connections.md))
   ```yaml
   # connections/zosmf_connection.yaml
   environments:
     live:
       type: member  # Changed from team
   ```

2. **Upload updated connection** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk connection upload connections/zosmf_connection.yaml --update
   ```

3. **Each user sets credentials** ([Guide 04](./04-uploading-with-adk.md))
   ```bash
   adk connection credentials set zosmf --environment live
   ```

---

## 🔍 Troubleshooting Guide

### Issue: Agent not following instructions

**Possible causes:**
- Instructions unclear or ambiguous
- Wrong LLM model selected
- Tool descriptions don't match usage

**Where to look:**
- [Understanding Agent Fields](./01-understanding-agent-fields.md) - Instructions section
- [Understanding Agent Fields](./01-understanding-agent-fields.md) - LLM selection
- [Understanding Tools](./02-understanding-tools.md) - Tool descriptions

---

### Issue: Authentication failures

**Possible causes:**
- Wrong credentials
- Missing permissions
- Connection misconfigured

**Where to look:**
- [Understanding Connections](./03-understanding-connections.md) - Authentication types
- [Understanding Connections](./03-understanding-connections.md) - Troubleshooting section
- [Uploading with ADK](./04-uploading-with-adk.md) - Credentials configuration

---

### Issue: Tool not found

**Possible causes:**
- Tool not uploaded
- Name mismatch between agent and tool
- Tool not linked to connection

**Where to look:**
- [Understanding Tools](./02-understanding-tools.md) - Tool-to-agent mapping
- [Uploading with ADK](./04-uploading-with-adk.md) - Upload order
- [Uploading with ADK](./04-uploading-with-adk.md) - Troubleshooting

---

### Issue: Cannot publish agent

**Possible causes:**
- Agent not tested in draft
- Dependencies missing in live
- Validation errors

**Where to look:**
- [Uploading with ADK](./04-uploading-with-adk.md) - Testing section
- [Uploading with ADK](./04-uploading-with-adk.md) - Publishing section
- [Uploading with ADK](./04-uploading-with-adk.md) - Troubleshooting

---

## 📖 Glossary

**ADK (Agent Development Kit)**: Command-line tool for managing watsonx Orchestrate agents, tools, and connections.

**Agent**: An AI-powered assistant that uses LLMs and tools to accomplish tasks.

**Connection**: Configuration that provides authentication and endpoint information for external systems.

**Draft Environment**: Development/testing environment where agents can be tested before production.

**IPL (Initial Program Load)**: The process of loading and starting a z/OS operating system.

**Live Environment**: Production environment where published agents are available to all users.

**LLM (Large Language Model)**: The AI model that powers the agent's reasoning and decision-making.

**OpenAPI Specification**: Standard format for describing REST APIs.

**Operation ID**: Unique identifier for a tool operation, used to reference tools in agents.

**React Style**: Reasoning pattern where the agent thinks, acts, observes, and repeats.

**Tool**: An API or function that an agent can use to interact with external systems.

**z/OSMF (z/OS Management Facility)**: IBM's web-based interface for managing z/OS systems.

---

## 🤝 Contributing

To improve this documentation:

1. **Found an error?** Please report it or submit a correction.
2. **Have a suggestion?** Share your ideas for improvement.
3. **Created something useful?** Consider adding it to the guides.

---

## 📚 Additional Resources

### IBM Documentation
- [watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [z/OSMF REST Services](https://www.ibm.com/docs/en/zos/2.5.0?topic=services-zosmf-rest-services)
- [Agent Development Kit Guide](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)

### Standards and Specifications
- [OpenAPI Specification](https://swagger.io/specification/)
- [YAML Syntax](https://yaml.org/spec/1.2/spec.html)
- [REST API Best Practices](https://restfulapi.net/)

### z/OS Resources
- [MVS System Commands](https://www.ibm.com/docs/en/zos/2.5.0?topic=commands-mvs-system)
- [TSO/E Commands](https://www.ibm.com/docs/en/zos/2.5.0?topic=commands-tsoe)
- [z/OS Security](https://www.ibm.com/docs/en/zos/2.5.0?topic=zos-security)

---

## 📝 Document Version

- **Version**: 1.0.0
- **Last Updated**: March 2026
- **Compatibility**: watsonx Orchestrate, z/OSMF 2.5+

---

## ✨ About

This documentation was created to help users understand and deploy the IPL-check custom agent for watsonx Orchestrate. The agent automates z/OS system health validation after IPL, checking critical subsystems and configurations.

**Created with Bob - AI Software Engineering Assistant**

---

## 📋 Documentation Checklist

Use this checklist to track your learning progress:

- [ ] Read Understanding Agent Fields guide
- [ ] Read Understanding Tools guide
- [ ] Read Understanding Connections guide
- [ ] Read Uploading with ADK guide
- [ ] Install and configure ADK
- [ ] Upload connections
- [ ] Upload tools
- [ ] Upload agent
- [ ] Test agent in draft
- [ ] Publish agent to live
- [ ] Train team on using the agent
- [ ] Document any customizations made

---

**Need help?** Start with the guide that matches your current task, or read them in order for a complete understanding.