from base.DatabaseDriver import *
from tables.ChildInstance import ChildInstance


class ChildInstanceDBEntry(Base):
    """
    Skeleton for a db entry in the "Child" table.

    Will be added into the database upon init
    """

    __tablename__ = "child"

    id = Column(Integer, primary_key = True, autoincrement = True)
    uuid = db.Column(db.String(Config.UUID_TOKEN_LENGTH), unique = True)
    firstname = Column(String(64))
    lastname = Column(String(64))

    classroom_id = Column(Integer, ForeignKey("classroom.id"))
    classroom = relationship('ClassroomInstanceDBEntry', foreign_keys = [classroom_id])

    teacher_id = Column(Integer, ForeignKey("teacher.id"))
    teacher = relationship('TeacherInstanceDBEntry', back_populates = "children", foreign_keys = [teacher_id])

    def __init__(self, childInstance: ChildInstance):
        self.firstname = childInstance.firstname
        self.lastname = childInstance.lastname
        self.age = childInstance.age
        self.uuid = secrets.token_urlsafe(Config.UUID_TOKEN_LENGTH)

    def __repr__(self):
        return "<ChildInstanceDBEntry(firstname='%s')>" % (
            self.firstname,
        )
