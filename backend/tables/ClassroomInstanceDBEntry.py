from tables.ClassroomInstance import ClassroomInstance

from base.DatabaseDriver import *


class ClassroomInstanceDBEntry(Base):
    """
    Skeleton for a db entry in the "classroom" table.

    Will be added into the database upon init
    """

    __tablename__ = "classroom"

    id = Column(Integer, primary_key = True, autoincrement = True)
    uuid = db.Column(db.String(Config.UUID_TOKEN_LENGTH), unique = True)
    name = Column(String(64))
    capacity = Column(Integer)

    facility_id = Column(Integer, ForeignKey("facility.id"))
    facility = relationship('FacilityInstanceDBEntry', foreign_keys = [facility_id])

    teachers = relationship("TeacherInstanceDBEntry", back_populates = "classroom")
    children = relationship("ChildInstanceDBEntry", back_populates = "classroom")

    _teacherids = Column(db.String(512), default = '')
    _badids = Column(db.String(512), default = '')

    @property
    def teacherids(self):
        return [int(x) for x in self._teacherids.split(';') if x]

    @teacherids.setter
    def teacherids(self, value):
        if str(value) in self._badids:
            self._teacherids.replace(f"{value};", '')
            self._badids.replace(f"{value};", '')
            return
        if value in self.teacherids:
            return
        self._teacherids += '%s;' % value

    @property
    def badids(self):
        return [int(x) for x in self._badids.split(';') if x]

    @badids.setter
    def badids(self, value):
        self._badids += '%s;' % value

    def __init__(self, classroomInstance: ClassroomInstance):
        self.name = classroomInstance.name
        self.capacity = classroomInstance.capacity
        self.uuid = secrets.token_urlsafe(Config.UUID_TOKEN_LENGTH)

    def __repr__(self):
        return "<ClassroomInstanceDBEntry(brand='%s')>" % (
            self.name,
        )
