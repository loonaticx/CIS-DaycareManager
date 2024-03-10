from uuid import uuid4

from tables.ClassroomInstance import ClassroomInstance
from tables.FacilityInstance import FacilityInstance

from base.DatabaseDriver import *
from tables.TeacherInstance import TeacherInstance


class TeacherInstanceDBEntry(Base):
    """
    Skeleton for a db entry in the "inventory" table.

    Will be added into the database upon init
    """

    __tablename__ = "teacher"

    id = Column(Integer, primary_key = True, autoincrement = True)
    firstname = Column(String(64))
    lastname = Column(String(64))
    uuid = db.Column(db.String(Config.UUID_TOKEN_LENGTH), unique = True)
    classroom_id = Column(Integer, ForeignKey("classroom.id"))
    # classroom_uuid = Column(db.String, ForeignKey("classroom.uuid", use_alter = True))
    classroom = relationship('ClassroomInstanceDBEntry', foreign_keys = [classroom_id])

    # classroom = relationship('ClassroomInstanceDBEntry', backref = 'classroom', lazy = 'dynamic',
    #                          foreign_keys = "[ClassroomInstanceDBEntry.id, ClassroomInstanceDBEntry.uuid]")

    # classroom = relationship('ClassroomInstanceDBEntry',  backref = 'classroom', lazy = 'dynamic', foreign_keys =
    # "[ClassroomInstanceDBEntry.id, ClassroomInstanceDBEntry.uuid]")
    children = relationship("ChildInstanceDBEntry", back_populates = "teacher")
    _childids = Column(db.String(512), default = '')

    @property
    def childids(self):
        return [int(x) for x in self._childids.split(';') if x]

    @childids.setter
    def childids(self, value):
        self._childids += '%s;' % value

    def __init__(self, teacherInstance: TeacherInstance):
        self.firstname = teacherInstance.firstname
        self.lastname = teacherInstance.lastname
        self.uuid = secrets.token_urlsafe(Config.UUID_TOKEN_LENGTH)

    def __repr__(self):
        return "<TeacherInstanceDBEntry(brand='%s')>" % (
            self.firstname,
        )
