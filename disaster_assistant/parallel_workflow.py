from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent

from .disaster_tools import (
    lookup_incident,
    lookup_relief_point,
)

MODEL = "gemini-3.5-flash-lite"


parallel_incident_agent = LlmAgent(
    name="parallel_incident_agent",
    model=MODEL,
    description="Looks up the supplied incident record independently.",
    instruction="""
You are the incident branch of a parallel disaster-information workflow.

Read the user's request.

Extract:
- area
- incident type, if the user supplied one

You MUST call lookup_incident.

Use only the values stated by the user.
Do not invent an area or incident type.

If lookup_incident returns found:
- report the supplied incident record clearly
- preserve incident_id, area, incident_type, status, priority,
  summary, recorded_update, source_id, effective_date, and data_status

If it returns needs_clarification:
- report the available incident types
- do not choose one yourself

If it returns not_found:
- clearly report that the supplied records contain no matching incident

Do not add general or live disaster information.
""",
    tools=[lookup_incident],
    output_key="parallel_incident_result",
)


parallel_relief_agent = LlmAgent(
    name="parallel_relief_agent",
    model=MODEL,
    description="Looks up the supplied relief-point record independently.",
    instruction="""
You are the relief branch of a parallel disaster-information workflow.

Read the user's request.

Extract:
- area
- assistance type, if the user supplied one

You MUST call lookup_relief_point.

Use only the values stated by the user.
Do not invent an area or assistance type.

If lookup_relief_point returns found:
- report the supplied relief record clearly
- preserve relief_id, area, assistance_type, name,
  location_description, services, recorded_status,
  source_id, effective_date, and data_status

If it returns needs_clarification:
- report the available assistance types
- do not choose one yourself

If it returns not_found:
- clearly report that the supplied records contain no matching relief point

Do not add phone numbers, websites, addresses, or live information
that were not returned by the supplied tool.
""",
    tools=[lookup_relief_point],
    output_key="parallel_relief_result",
)


parallel_incident_relief_workflow = ParallelAgent(
    name="parallel_incident_relief_workflow",
    description=(
        "Runs incident and relief-point lookups independently "
        "for a combined information request."
    ),
    sub_agents=[
        parallel_incident_agent,
        parallel_relief_agent,
    ],
)
