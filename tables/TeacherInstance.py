from dataclasses import dataclass

from tables import ClassroomInstanceDBEntry


@dataclass
class TeacherInstance:
    """
    A local Teacher instance, not dependent on the database.
    """
    firstname: str = ""
    lastname: str = ""
    room: ClassroomInstanceDBEntry = None

