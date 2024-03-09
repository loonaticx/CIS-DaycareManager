
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

    classroom_id = Column(Integer, ForeignKey("classroom.id"))
    classroom = relationship('ClassroomInstanceDBEntry', foreign_keys = [classroom_id])

    children = relationship("ChildInstanceDBEntry", back_populates = "teacher")
    _childids = Column(db.String, default='')
    @property
    def childids(self):
        return [int(x) for x in self._childids.split(';')]
    @childids.setter
    def childids(self, value):
        self._childids += '%s;' % value


    def __init__(self, teacherInstance: TeacherInstance):
        self.firstname = teacherInstance.firstname
        self.lastname = teacherInstance.lastname


    def __repr__(self):
        return "<TeacherInstanceDBEntry(brand='%s')>" % (
            self.name,
        )
