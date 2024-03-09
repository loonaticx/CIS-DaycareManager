from dataclasses import dataclass, field

from tables import ClassroomInstanceDBEntry
from tables.ChildInstance import ChildInstance


@dataclass
class TeacherInstance:
    """
    A local "Inventory" object, not dependent on the database.
    """
    firstname: str = ""
    lastname: str = ""
    room: ClassroomInstanceDBEntry = None
    # currentChildren: list[ChildInstance] = field(default_factory=list)

