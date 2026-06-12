from app.models import Property


def seed_properties() -> list[Property]:
    return [
        Property(
            id="prop-a",
            name="Property A",
            address="12 Market Street, London",
            status="healthy",
            notes="Executive short-let with upcoming guest arrival.",
        ),
        Property(
            id="prop-b",
            name="Property B",
            address="4 Riverside Walk, Manchester",
            status="attention",
            notes="Power issue reported by current guest. Emergency repair may be needed.",
        ),
        Property(
            id="prop-c",
            name="Property C",
            address="77 Harbour Road, Bristol",
            status="healthy",
            notes="Routine turnover completed.",
        ),
    ]

