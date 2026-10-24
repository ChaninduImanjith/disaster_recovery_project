import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data_pack"


def _read_csv(filename: str) -> list[dict]:
    """Read a CSV file from the supplied data pack."""
    file_path = DATA_DIR / filename

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _normalize(value: str) -> str:
    """Normalize user text for simple record matching."""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def classify_issue(description: str) -> dict:
    """
    Classify a reported disaster issue using only issue_rules.csv.

    Args:
        description: Short description of the user's problem.

    Returns:
        A dictionary containing the matched category, priority,
        recommended action, and supplied source information.
    """
    if not description or not description.strip():
        return {
            "status": "missing_information",
            "message": "A short description of the problem is required."
        }

    user_text = description.strip().lower()
    rules = _read_csv("issue_rules.csv")

    for rule in rules:
        keywords = [
            keyword.strip().lower()
            for keyword in rule["keywords"].split("|")
            if keyword.strip()
        ]

        matched_keywords = [
            keyword for keyword in keywords
            if keyword in user_text
        ]

        if matched_keywords:
            return {
                "status": "found",
                "rule_id": rule["rule_id"],
                "category": rule["category"],
                "priority": rule["priority"],
                "recommended_action": rule["recommended_action"],
                "matched_keywords": matched_keywords,
                "source_id": rule["source_id"],
                "effective_date": rule["effective_date"],
                "data_status": rule["data_status"],
            }

    return {
        "status": "not_found",
        "message": "The supplied issue rules do not classify this description."
    }


def lookup_incident(area: str, incident_type: str = "") -> dict:
    """
    Look up incident records using only incident_status.csv.

    Args:
        area: Area name such as Colombo, Ratnapura, or Kegalle.
        incident_type: Optional incident type such as flood,
            landslide, or blocked_route.

    Returns:
        A matching incident record, a clarification result when
        more than one incident is possible, or a not-found result.
    """
    if not area or not area.strip():
        return {
            "status": "missing_information",
            "message": "Area is required."
        }

    records = _read_csv("incident_status.csv")
    normalized_area = _normalize(area)

    area_matches = [
        row for row in records
        if _normalize(row["area"]) == normalized_area
    ]

    if not area_matches:
        return {
            "status": "not_found",
            "message": f"No supplied incident record was found for area '{area}'."
        }

    if incident_type and incident_type.strip():
        normalized_type = _normalize(incident_type)

        matches = [
            row for row in area_matches
            if _normalize(row["incident_type"]) == normalized_type
        ]

        if not matches:
            return {
                "status": "not_found",
                "message": (
                    f"No supplied incident record was found for area "
                    f"'{area}' and incident type '{incident_type}'."
                )
            }

        return {
            "status": "found",
            "record": matches[0]
        }

    incident_types = sorted(
        {row["incident_type"] for row in area_matches}
    )

    if len(area_matches) > 1:
        return {
            "status": "needs_clarification",
            "message": "More than one supplied incident exists for this area.",
            "area": area_matches[0]["area"],
            "incident_types": incident_types
        }

    return {
        "status": "found",
        "record": area_matches[0]
    }


def lookup_safety_guidance(
    incident_type: str,
    priority: str = ""
) -> dict:
    """
    Look up recorded safety guidance using only safety_guidance.csv.

    Args:
        incident_type: Incident type such as flood, landslide,
            or blocked_route.
        priority: Optional priority such as high, urgent, or critical.

    Returns:
        Matching supplied safety guidance, a clarification result,
        or a not-found result.
    """
    if not incident_type or not incident_type.strip():
        return {
            "status": "missing_information",
            "message": "Incident type is required."
        }

    records = _read_csv("safety_guidance.csv")
    normalized_type = _normalize(incident_type)

    type_matches = [
        row for row in records
        if _normalize(row["incident_type"]) == normalized_type
    ]

    if not type_matches:
        return {
            "status": "not_found",
            "message": (
                f"No supplied safety guidance was found for "
                f"incident type '{incident_type}'."
            )
        }

    if priority and priority.strip():
        normalized_priority = _normalize(priority)

        matches = [
            row for row in type_matches
            if _normalize(row["priority"]) == normalized_priority
        ]

        if not matches:
            return {
                "status": "not_found",
                "message": (
                    f"No supplied safety guidance was found for "
                    f"incident type '{incident_type}' with priority "
                    f"'{priority}'."
                )
            }

        return {
            "status": "found",
            "record": matches[0]
        }

    priorities = sorted(
        {row["priority"] for row in type_matches}
    )

    if len(type_matches) > 1:
        return {
            "status": "needs_clarification",
            "message": (
                "More than one supplied safety-guidance record "
                "matches this incident type."
            ),
            "incident_type": incident_type,
            "priorities": priorities
        }

    return {
        "status": "found",
        "record": type_matches[0]
    }


def lookup_relief_point(
    area: str,
    assistance_type: str = ""
) -> dict:
    """
    Look up relief points using only relief_points.csv.

    Args:
        area: Area name such as Colombo, Ratnapura, or Kegalle.
        assistance_type: Optional assistance type such as
            temporary_shelter, information_point, or relief_supplies.

    Returns:
        A matching relief point, a clarification result when
        multiple choices exist, or a not-found result.
    """
    if not area or not area.strip():
        return {
            "status": "missing_information",
            "message": "Area is required."
        }

    records = _read_csv("relief_points.csv")
    normalized_area = _normalize(area)

    area_matches = [
        row for row in records
        if _normalize(row["area"]) == normalized_area
    ]

    if not area_matches:
        return {
            "status": "not_found",
            "message": f"No supplied relief point was found for area '{area}'."
        }

    if assistance_type and assistance_type.strip():
        normalized_type = _normalize(assistance_type)

        matches = [
            row for row in area_matches
            if _normalize(row["assistance_type"]) == normalized_type
        ]

        if not matches:
            return {
                "status": "not_found",
                "message": (
                    f"No supplied relief point was found for area "
                    f"'{area}' and assistance type '{assistance_type}'."
                )
            }

        return {
            "status": "found",
            "record": matches[0]
        }

    assistance_types = sorted(
        {row["assistance_type"] for row in area_matches}
    )

    if len(area_matches) > 1:
        return {
            "status": "needs_clarification",
            "message": "More than one supplied relief point exists for this area.",
            "area": area_matches[0]["area"],
            "assistance_types": assistance_types
        }

    return {
        "status": "found",
        "record": area_matches[0]
    }


def route_request(user_message: str) -> dict:
    """
    Determine which workflow should handle the user's request.

    Args:
        user_message: The original user request.

    Returns:
        A dictionary containing the required workflow route.
    """
    if not user_message or not user_message.strip():
        return {
            "status": "missing_information",
            "route": "clarification_loop_workflow",
            "reason": "No request text was supplied."
        }

    text = user_message.lower()

    unsupported_action_terms = [
        "reserve",
        "book",
        "booking",
        "dispatch",
        "send rescue",
        "arrange transport",
        "process payment",
        "make payment",
        "official complaint",
    ]

    if any(term in text for term in unsupported_action_terms):
        return {
            "status": "unsupported",
            "route": "unsupported_request",
            "reason": (
                "The requested action is outside the assistant's "
                "supported capabilities."
            )
        }

    explicit_incident_types = [
        "flood",
        "floodwater",
        "landslide",
        "blocked route",
        "blocked_route",
        "route blocked",
        "road blocked",
    ]

    relief_terms = [
        "shelter",
        "relief",
        "assistance point",
        "assistance",
        "temporary shelter",
        "information point",
        "relief supplies",
    ]

    incident_terms = [
        "incident",
        "status",
        "disaster",
    ]

    has_explicit_incident = any(
        term in text for term in explicit_incident_types
    )

    has_relief_request = any(
        term in text for term in relief_terms
    )

    has_incident_request = any(
        term in text for term in incident_terms
    )

    normalized_message = (
        text.strip()
        .replace("-", "_")
        .replace(" ", "_")
    )

    # A short incident-type-only message is treated as the answer
    # to a previous clarification question.
    if normalized_message in {"flood", "landslide", "blocked_route"}:
        return {
            "status": "found",
            "route": "clarification_loop_workflow",
            "reason": (
                "The message contains only an incident type and is treated "
                "as a clarification response."
            )
        }

    if has_relief_request and has_explicit_incident:
        return {
            "status": "found",
            "route": "parallel_incident_relief_workflow",
            "reason": (
                "The request contains both explicit incident "
                "information and relief/assistance information."
            )
        }

    if has_explicit_incident:
        return {
            "status": "found",
            "route": "sequential_incident_workflow",
            "reason": "The incident type is explicitly stated."
        }

    if has_incident_request:
        return {
            "status": "found",
            "route": "clarification_loop_workflow",
            "reason": (
                "The user asks for incident information without "
                "providing an explicit incident type."
            )
        }

    return {
        "status": "found",
        "route": "clarification_loop_workflow",
        "reason": "The request requires clarification before lookup."
    }
