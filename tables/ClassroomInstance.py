from dataclasses import dataclass

from tables.FacilityInstance import FacilityInstance


@dataclass
class ClassroomInstance:
    """
    A local "Inventory" object, not dependent on the database.
    """
    name: str = "Unknown"
    capacity: int = 0
    facility: FacilityInstance = None

