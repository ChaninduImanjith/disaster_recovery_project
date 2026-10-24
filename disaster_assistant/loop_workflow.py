from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.loop_agent import LoopAgent

from google.adk.tools.get_user_choice_tool import get_user_choice
from google.adk.tools.exit_loop_tool import exit_loop

from .disaster_tools import lookup_incident


MODEL = "gemini-3.5-flash-lite"


# ---------------------------------------------------------
# CLARIFICATION / LOOKUP AGENT
# ---------------------------------------------------------
clarification_agent = LlmAgent(
    name="clarification_agent",
    model=MODEL,
    description=(
        "Obtains one missing incident type without guessing "
        "and retrieves the supplied incident record."
    ),
    instruction="""
You are the clarification stage for a disaster incident request.

Use the current message together with the immediately preceding
conversation context.

IMPORTANT CONTEXT RULE:
If the current user message contains only:
- flood
- landslide
- blocked_route

then treat it as the answer to the previous clarification question
and reuse the area from the previous incident request.

PROCESS:

1. Identify the area from the current request or the immediately
   preceding incident request.

2. If the user has not supplied an incident type:
   - call lookup_incident using only the area.

3. If lookup_incident returns needs_clarification:
   - use exactly the incident_types returned by the tool
   - call get_user_choice with those options
   - ask only one focused clarification question
   - never select an incident type yourself

4. If the user supplied an incident type, including a short follow-up
   such as "flood":
   - call lookup_incident using the remembered area and incident type

5. If lookup_incident returns found:
   give a clear response containing:
   - Incident ID
   - Area
   - Incident Type
   - Status
   - Priority
   - Summary
   - Recorded Update
   - Source ID
   - Effective Date
   - Data Status

   Clearly state that it is a supplied assignment record,
   not live disaster information.

6. If lookup_incident returns not_found:
   clearly report the supplied-record not-found result.

Never invent information.

IMPORTANT:
Do NOT call exit_loop yourself.
The loop control agent handles loop termination.
""",
    tools=[
        lookup_incident,
        get_user_choice,
    ],
    output_key="clarification_result",
)


# ---------------------------------------------------------
# LOOP CONTROL AGENT
# ---------------------------------------------------------
loop_control_agent = LlmAgent(
    name="loop_control_agent",
    model=MODEL,
    description="Stops the clarification loop after a final result is available.",
    instruction="""
Review the clarification result below:

{clarification_result?}

If the clarification result is empty or missing:
- do NOT call exit_loop
- the workflow is waiting for the user's clarification

If the clarification result contains a final incident record
or a clear not-found result:
- call exit_loop
- do not invent or change the result

If the clarification result is waiting for the user to choose an
incident type:
- do not call exit_loop
- do not invent a choice
""",
    tools=[
        exit_loop,
    ],
)


# ---------------------------------------------------------
# LOOP WORKFLOW
# ---------------------------------------------------------
clarification_loop_workflow = LoopAgent(
    name="clarification_loop_workflow",
    description=(
        "Use when an incident request is missing its incident type. "
        "Obtains one focused clarification and performs the lookup "
        "with a maximum of two iterations."
    ),
    sub_agents=[
        clarification_agent,
        loop_control_agent,
    ],
    max_iterations=2,
)
