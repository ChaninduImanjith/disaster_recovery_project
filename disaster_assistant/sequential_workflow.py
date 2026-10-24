from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent

from .disaster_tools import (
    classify_issue,
    lookup_incident,
    lookup_safety_guidance,
)

PRIMARY_MODEL = "gemini-3.5-flash-lite"
SECONDARY_MODEL = "gemini-3.5-flash-lite"


# ---------------------------------------------------------
# 1. INTAKE AGENT
# ---------------------------------------------------------
intake_agent = LlmAgent(
    name="intake_agent",
    model=PRIMARY_MODEL,
    description="Extracts the information required from the user's disaster request.",
    instruction="""
You are the intake stage of a disaster recovery workflow.

Read the user's request and extract only the supplied information.

Identify:
- area
- problem description
- requested information

Supported areas are:
- Colombo
- Ratnapura
- Kegalle

Do not invent missing information.

Return a short structured result in this format:

Area: <area or MISSING>
Description: <user's problem description>
Request: <incident_status, safety_guidance, or incident_and_safety>
""",
    output_key="intake_result",
)


# ---------------------------------------------------------
# 2. CLASSIFICATION AGENT
# ---------------------------------------------------------
classification_agent = LlmAgent(
    name="classification_agent",
    model=SECONDARY_MODEL,
    description="Classifies the reported problem using the supplied issue rules.",
    instruction="""
You are the classification stage.

The intake result is:

{intake_result}

You MUST use the classify_issue Function tool to classify
the problem description.

Do not classify from your own knowledge.

After calling the tool, return its result clearly, including:
- status
- category
- priority
- recommended_action
- source_id
- effective_date
- data_status

Do not invent any values.
""",
    tools=[classify_issue],
    output_key="classification_result",
)


# ---------------------------------------------------------
# 3. INCIDENT LOOKUP AGENT
# ---------------------------------------------------------
incident_lookup_agent = LlmAgent(
    name="incident_lookup_agent",
    model=SECONDARY_MODEL,
    description="Retrieves the matching supplied incident record.",
    instruction="""
You are the incident lookup stage.

Intake result:

{intake_result}

Classification result:

{classification_result}

You MUST use lookup_incident.

Use:
- the area from the intake result
- the classified incident category as incident_type

If the classification category is immediate_danger,
use the incident type explicitly described by the user when available.

Never invent an incident.

Return the tool result clearly and preserve all returned fields,
especially:
- incident_id
- area
- incident_type
- status
- priority
- summary
- recorded_update
- source_id
- effective_date
- data_status

If the tool returns needs_clarification or not_found,
preserve that result exactly and do not guess.
""",
    tools=[lookup_incident],
    output_key="incident_result",
)


# ---------------------------------------------------------
# 4. RESPONSE AGENT
# ---------------------------------------------------------
response_agent = LlmAgent(
    name="response_agent",
    model=PRIMARY_MODEL,
    description="Retrieves matching safety guidance and produces the final supplied-record response.",
    instruction="""
You are the final response stage.

Intake result:

{intake_result}

Classification result:

{classification_result}

Incident result:

{incident_result}

If the incident result is found:

1. Read the incident_type and priority from the incident result.
2. You MUST call lookup_safety_guidance using BOTH:
   - incident_type
   - priority
3. Use only the returned incident and safety records.

Give the user:
- recorded incident status
- priority
- incident summary
- recorded safety guidance
- what to avoid
- escalation note
- source IDs
- effective date
- data status

Clearly state that these are supplied assignment records,
not live disaster information.

If a previous stage returned needs_clarification,
ask one focused question and do not guess.

If a previous stage returned not_found,
give a clear not-found result.

Do not add phone numbers, websites, locations, safety instructions,
or other facts that were not returned by the supplied tools.
""",
    tools=[lookup_safety_guidance],
    output_key="sequential_response",
)


# ---------------------------------------------------------
# SEQUENTIAL WORKFLOW
# ---------------------------------------------------------
sequential_incident_workflow = SequentialAgent(
    name="sequential_incident_workflow",
    description=(
        "Use ONLY when the incident type is already clearly provided by the user. "
        "Runs intake, classification, incident lookup, and response in sequence. "
        "Do NOT use when the incident type is missing or ambiguous."
    ),
    sub_agents=[
        intake_agent,
        classification_agent,
        incident_lookup_agent,
        response_agent,
    ],
)
