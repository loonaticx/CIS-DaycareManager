from dataclasses import dataclass, field


@dataclass
class FacilityInstance:
    """
    A local facility instance, not dependent on the database.
    """
    name: str = "Unknown"
    classrooms: list = field(default_factory = list)
