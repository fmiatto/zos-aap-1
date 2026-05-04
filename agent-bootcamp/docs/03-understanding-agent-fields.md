# Understanding IPL-check Agent Fields

Now that you have your connections and tools created, you can start building your agent! Agent files are the core of your agent and are responsible for defining the behavior of your agent. Let's create your first agent framework:

First, create a new file called `IPL-check-agent.yaml` Open your Terminal or Command Line and run the following commands:
```
touch IPL-check-agent.yaml
```
second, open IPL_Validator.yaml in your favorite text editor
```
open IPL-check-agent.yaml
```

## Complete Agent File Structure
Copy and paste the following code in IPL-check-agent.yaml
```yaml
spec_version: v1
kind: native
name: IPL_Validator
description: Agent that runs through a series of checks to make sure systems are healthy after an IPL
instructions: |
  You are going to run a series of commands using your tools to verify configurations after an IPL on a z/OS. You will follow the steps in order. You will print out to the user what number step you are running, what you high level action you will perform (ex- checking what IPL pack the system is on by running D IPLINFO), and the full output of the step in a pretty format. ALWAYS INCLUDE THE FULL OUTPUT OF EACH COMMAND.

  DO NOT GUESS. DO NOT SPECULATE. ONLY USE THE INFORMATION RETURNED FROM RUNNING YOUR TOOLS


  STEP 1. check to make sure you are on the right IPL pack. run your Issue an operator command from the system console tool using the command "D IPLINFO".  Extract the value inside CURRENT IPL DEVICE from the response
  Print out the full output. Format the response prettily.
  STOP AND WAIT FOR THE OUTPUT TO BE FULLY FORMATTED PRETTILY AND PRINTED TO THE USER 


  Step 2. check to make sure TSO is running. run your Execute TSO command in an existing TSO address space tool using the default command TIME. If you get "message": "READY " in your response,  TSO is running. 
  Print out the full response. Format the full response prettily
  STOP AND WAIT FOR THE OUTPUT TO BE FULLY FORMATTED PRETTILY AND PRINTED TO THE USER 


  Step 3. Check that OMVS is running. run your Issue an operator command from the system console tool using the command "D OMVS". 
  Print out the full response. Format the full response prettily
  STOP AND WAIT FOR THE OUTPUT TO BE FULLY FORMATTED PRETTILY AND PRINTED TO THE USER 

  Step 4. Check to see if there are any mount failures on OMVS. run your Issue an operator command from the system console tool using the command "D OMVS,MF". If there are errors, print out which mount file paths have failed. Also, print out the full response. Format the full response prettily
  STOP AND WAIT FOR THE OUTPUT TO BE FULLY FORMATTED PRETTILY AND PRINTED TO THE USER 

  Step 5. Check to see if zosmf is working. If you were able to run any of the previous 1-4 steps, we know zosmf is working because your tools utilize zosmf api. If the other steps ran, report that zOSMF is working

  Step 6.  check to see JES is running. Run your Issue an operator command from the system console tool using  the command "$D JES2"
  Print out the full response. Format the full response prettily
  STOP AND WAIT FOR THE OUTPUT TO BE FULLY FORMATTED PRETTILY AND PRINTED TO THE USER 

  Step 7. Finished. Print out summary of the previous outputs. Format prettily.
llm: watsonx/meta-llama/llama-3-3-70b-instruct
style: react
collaborators: []
tools: 
- sendOperatorCommand
- executeTsoCommand
```

## Upload agent to Orchestrate
You have all the code you need to make this agent! Now all that's left is to upload it to Orchestrate. To do that, run the following command:
```
 orchestrate agents import --file IPL-check-agent.yaml
```

Done! You can proceed on to the next section now or scroll down to the Dive Deeper section to learn more about what each field means and best practices.
- [Test your new agent!](./04-testing-your-new-agent.md) - Testing your new agent in watsonx Orchestrate

---

## Dive Deeper
### Field-by-Field Explanation

#### `spec_version: v1`

**What it is:** The version of the agent specification format being used.

**Purpose:** Tells watsonx Orchestrate which version of the agent configuration schema to use when parsing this file.

---

#### `kind: native`

**What it is:** The type of agent being defined.

**Purpose:** Specifies whether this is a native watsonx agent or another type of integration.

**Valid values:**
- `native` - native agents are built and defined for watsonx Orchestrate. (most common)
- `external` - external agents are built outside watsonx Orchestrate and can be used as collaborators for native agents. (less common)

**When to use:**
- Use `native` for agents that will run within watsonx Orchestrate using its LLM capabilities
- Use `external` only when integrating pre-existing agent systems

---

#### `name: IPL_Validator`

**What it is:** The unique identifier and display name for your agent.

**Purpose:** 
- Identifies the agent in the watsonx Orchestrate UI
- Used when referencing this agent from other agents or workflows
- Appears in logs and monitoring

**Naming conventions:**
- Use alphanumeric characters and underscores
- No spaces (use underscores instead)
- Should be descriptive and unique
- CamelCase or snake_case recommended

**Examples:**
```yaml
name: IPL_Validator          # Good - descriptive and clear
name: System_Health_Checker  # Good - describes purpose
name: agent1                 # Bad - not descriptive
name: IPL Validator          # Bad - contains space
```

---

#### `description: Agent that runs through a series of checks...`

**What it is:** A human-readable description of what the agent does.

**Purpose:**
- Helps users understand the agent's purpose
- Appears in the watsonx Orchestrate UI
- Used for documentation and discovery
- May be used by the LLM for context

**Best practices:**
- Keep it concise but informative (1-2 sentences)
- Describe WHAT the agent does, not HOW
- Use clear, non-technical language when possible
- Mention the main use case or problem it solves

**Examples:**
```yaml
# Good - clear and specific
description: Agent that runs through a series of checks to make sure systems are healthy after an IPL

# Good - describes purpose and outcome
description: Validates z/OS system health after IPL by checking critical subsystems and configurations

# Too vague
description: System checker agent

# Too technical/detailed
description: Uses z/OSMF REST APIs to execute D IPLINFO, TIME, D OMVS, and D OMVS,MF commands
```

---

#### `instructions: |`

**What it is:** Multi-line instructions that tell the agent HOW to accomplish its task.
This is the most critical field in your custom agent. It's the LLM's job to parse these instructions and execute the agent's task. 

**Purpose:**
- Provides step-by-step guidance to the LLM
- Defines the workflow and logic
- Specifies which tools to use and when
- Sets output formatting requirements

**Structure:**
The `|` character indicates a multi-line YAML string. Everything indented below it is part of the instructions.

**Best practices:**
- Number your steps clearly (Step 1, Step 2, etc.)
- Be explicit about which tool to use
- Specify exact commands to execute if possible
- Define success criteria
- Include formatting instructions
- Use clear, imperative language

---

#### `llm: watsonx/meta-llama/llama-3-3-70b-instruct`

**What it is:** The Large Language Model that will power the agent's reasoning and decision-making. Only llama-3-3-70b-instruct and watsonx/ibm/granite-3-3-8b-instruct 
are officially supported by watsonx Assistant for Z at this time.

**Purpose:**
- Determines which AI model processes the instructions
- Affects the agent's capabilities, speed, and cost
- Different models have different strengths

---

#### `style: react`

**What it is:** The reasoning pattern the agent uses to solve problems.

**Purpose:** Defines how the agent thinks through problems and decides which actions to take.

**Valid values:**

1. **`react`** (Reasoning and Acting)
   - Agent reasons about what to do, then acts
   - Iterative: think → act → observe → think → act
   - Best for: Multi-step tasks, complex workflows, decision-making
   - Example: "I need to check IPL info, so I'll use the operator command tool"

2. **`default`**
   - Relies on the models intrinsic ability to understand, plan and call tools and knowledge.
   - More deterministic and predictable
   - Best for: Simple, direct tool invocations
   - Example: User says "check IPL" → agent immediately calls D IPLINFO


**For IPL-check agent:**
```yaml
style: react
```
This is appropriate because the agent needs to:
- Reason through multiple steps
- Decide which tool to use at each step
- Interpret results before proceeding
- Handle errors and adapt

---

#### `collaborators: []`

**What it is:** A list of other agents this agent can work with or delegate tasks to.

**Purpose:**
- Enables multi-agent workflows
- Allows task delegation to specialized agents
- Creates agent hierarchies (coordinator → specialist agents)

**Example Format for future agents:**
```yaml
# Empty list (no collaborators)
collaborators: []

# With collaborators
collaborators:
  - dataset_agent
  - job_submission_agent
  - security_checker
```

**For IPL-check agent:**
```yaml
collaborators: []
```
This agent works independently and doesn't need to delegate to other agents.

**When to add collaborators:**

Example of an agent that WOULD use collaborators:
```yaml
name: System_Coordinator
collaborators:
  - IPL_Validator        # Delegates IPL checks
  - Performance_Monitor  # Delegates performance analysis
  - Security_Auditor     # Delegates security checks
instructions: |
  You coordinate system health checks by delegating to specialist agents.
  1. Ask IPL_Validator to check system health after IPL
  2. Ask Performance_Monitor to analyze system performance
  3. Ask Security_Auditor to verify security configurations
  4. Compile results and report to user
```
---

#### `tools:`

**What it is:** A list of tools (APIs, scripts, agentic workflows) the agent can use to accomplish tasks.

**Purpose:**
- Defines the agent's capabilities
- Links to tool definitions (OpenAPI specs)
- Determines what actions the agent can take

**Format:**
```yaml
tools: 
  - sendOperatorCommand
  - executeTsoCommand
```

**How tools are referenced:**
1. Tool names must match the `operationId` in the OpenAPI spec
2. Tools must be uploaded to watsonx Orchestrate before the agent
3. Tools must be connected to appropriate connections (credentials)

**Tool selection best practices:**
- Only include tools the agent actually needs
- Too many tools can confuse the LLM
- Group related functionality into single tools when possible
- Ensure tools have clear, descriptive names

---

### Complete Example with Annotations

```yaml
# Specification version - always v1 for now
spec_version: v1

# Agent type - native means it runs in watsonx Orchestrate
kind: native

# Unique identifier - no spaces, descriptive
name: IPL_Validator

# User-friendly description - what does it do?
description: Agent that runs through a series of checks to make sure systems are healthy after an IPL

# Detailed instructions - the agent's "playbook"
instructions: |
  # Context: What is the agent's role?
  You are going to run a series of commands using your tools to verify 
  configurations after an IPL on a z/OS.
  
  # Workflow: How should it work?
  You will follow the steps in order.
  
  # Output: What should the user see?
  You will print out to the user what number step you are running, what you 
  high level action you will perform, and the full output of the step in a 
  pretty format.

  # Step 1: Specific action with tool and command
  STEP 1. check to make sure you are on the right IPL pack. 
  run your Issue an operator command from the system console tool 
  using the command "D IPLINFO". 
  Extract the value inside CURRENT IPL DEVICE from the response
  Print out the full output. Format the response prettily.

  # Step 2: Another action with success criteria
  Step 2. check to make sure TSO is running. 
  run your Execute TSO command in an existing TSO address space tool 
  using the default command TIME. 
  If you get "message": "READY " in your response, TSO is running. 
  Print out the full response. Format the full response prettily

  # Steps 3-4: Additional checks
  Step 3. Check that OMVS is running. 
  run your Issue an operator command from the system console tool 
  using the command "D OMVS". 
  Print out the full response. Format the full response prettily

  Step 4. Make sure there are no mount failures on OMVS. 
  run your Issue an operator command from the system console tool 
  using the command "D OMVS,MF"
  Print out the full response. Format the full response prettily

# LLM: Which AI model powers this agent?
llm: watsonx/meta-llama/llama-3-3-70b-instruct

# Style: How does the agent think?
style: react

# Collaborators: Other agents this can work with (none for this agent)
collaborators: []

# Tools: What can this agent do?
tools: 
  - sendOperatorCommand    # Issue MVS operator commands
  - executeTsoCommand      # Execute TSO commands
```

---

### Quick Reference

| Field | Required? | Common Values | Purpose |
|-------|-----------|---------------|---------|
| `spec_version` | Yes | `v1` | Schema version |
| `kind` | Yes | `native`, `external` | Agent type |
| `name` | Yes | Any unique name | Agent identifier |
| `description` | Yes | Any text | User-facing description |
| `instructions` | Yes | Multi-line text | Agent's playbook |
| `llm` | Yes | Model path | AI model to use |
| `style` | Yes | `react`, `function_calling`, `conversational` | Reasoning pattern |
| `collaborators` | Yes | List of agent names or `[]` | Other agents to work with |
| `tools` | Yes | List of tool names | Available capabilities |


---
### Tips for Modifying the Agent

#### To add a new validation step:

1. Add to the `instructions` field:
```yaml
instructions: |
  ...existing steps...
  
  Step 8. Check JES2 status. run your Issue an operator command from 
  the system console tool using the command "D A,JES2"
  Print out the full response. Format the full response prettily
```

#### To use a different model:

```yaml
# Change from:
llm: watsonx/meta-llama/llama-3-3-70b-instruct

# To:
llm: watsonx/ibm/granite-3-3-8b-instruct
```

#### To add error handling:

```yaml
instructions: |
  ...existing steps...
  
  If any step fails:
  - Report the error message clearly
  - Indicate which step failed
  - Suggest possible remediation
  - Continue with remaining steps if possible
```
---

## Next Steps

- [Test your new agent!](./04-testing-your-new-agent.md) - Test your agent

---