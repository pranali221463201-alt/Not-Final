from .global_event_repository import add_event


def load_global_events():
    """
    Register predefined geopolitical risk events.
    """

    events = [

        {
            "event_id": "GEO-001",
            "event_type": "Port Disruption",
            "risk_score": 75,
            "risk_level": "High",

            "affected_regions": ["Mumbai", "Gujarat Coast"],
            "affects": ["suppliers", "routes"],

            "valid_from": "2026-03-01",
            "valid_to": "2026-05-01"
        },

        {
            "event_id": "GEO-002",
            "event_type": "Regional Supply Chain Disruption",
            "risk_score": 80,
            "risk_level": "High",

            "affected_regions": ["Madhya Pradesh", "Bhopal"],
            "affects": ["suppliers", "manufacturing"],

            "valid_from": "2026-03-01",
            "valid_to": "2026-06-01"
        },

        {
            "event_id": "GEO-003",
            "event_type": "Transportation Disruption",
            "risk_score": 65,
            "risk_level": "Medium",

            "affected_regions": ["Maharashtra", "Pune", "Nagpur"],
            "affects": ["routes", "logistics"],

            "valid_from": "2026-03-05",
            "valid_to": "2026-04-10"
        },

        {
            "event_id": "GEO-004",
            "event_type": "Manufacturing Facility Impact",
            "risk_score": 55,
            "risk_level": "Medium",

            "affected_regions": ["Gujarat", "Ahmedabad", "Surat"],
            "affects": ["suppliers"],

            "valid_from": "2026-03-10",
            "valid_to": "2026-04-15"
        },

        {
            "event_id": "GEO-005",
            "event_type": "Regional Supply Shortage",
            "risk_score": 60,
            "risk_level": "Medium",

            "affected_regions": ["Indore", "Madhya Pradesh"],
            "affects": ["suppliers", "materials"],

            "valid_from": "2026-03-15",
            "valid_to": "2026-05-10"
        }

    ]

    for event in events:
        add_event(event)