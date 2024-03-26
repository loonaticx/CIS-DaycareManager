from dataclasses import dataclass

from tables.ClassroomInstance import ClassroomInstance


@dataclass
class ChildInstance:
    """
    A local child instance, not dependent on the database.
    """
    firstname: str = ""
    lastname: str = ""
    age: int = 0
    room: ClassroomInstance = None
