from dataclasses import dataclass

from tables.ClassroomInstance import ClassroomInstance
from tables.FacilityInstance import FacilityInstance


@dataclass
class ChildInstance:
    """
    A local "Inventory" object, not dependent on the database.
    """
    firstname: str = ""
    lastname: str = ""
    age: int = 0
    room: ClassroomInstance = None

