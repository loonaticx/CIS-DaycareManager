from dataclasses import dataclass, field


@dataclass
class FacilityInstance:
    """
    A local "Inventory" object, not dependent on the database.
    """
    name: str = "Unknown"
    classrooms: list = field(default_factory = list)
