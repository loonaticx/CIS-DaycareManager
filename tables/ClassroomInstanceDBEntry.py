from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint

from tables.ClassroomInstance import ClassroomInstance
# from tables.FacilityInstanceDBEntry import FacilityInstanceDBEntry

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

from base.DatabaseDriver import *


class ClassroomInstanceDBEntry(Base):
    """
    Skeleton for a db entry in the "classroom" table.

    Will be added into the database upon init
    """

    __tablename__ = "classroom"

    id = Column(Integer, primary_key = True, autoincrement = True)
    uuid = db.Column(db.String(Config.UUID_TOKEN_LENGTH), unique=True)
    name = Column(String(64))
    capacity = Column(Integer)

    facility_id = Column(Integer, ForeignKey("facility.id"))
    facility = relationship('FacilityInstanceDBEntry', foreign_keys = [facility_id])

    teachers = relationship("TeacherInstanceDBEntry", back_populates = "classroom")
    children = relationship("ChildInstanceDBEntry", back_populates = "classroom")
    #
    # ForeignKeyConstraint(
    #     ["id", "uuid"],
    #     ["classroom.id", "classroom.uuid"],
    #     onupdate="CASCADE",
    #     ondelete="SET NULL",
    # ),

    _teacherids = Column(db.String(512), default = '')

    @property
    def teacherids(self):
        return [int(x) for x in self._teacherids.split(';') if x]
    @teacherids.setter
    def teacherids(self, value):
        self._teacherids += '%s;' % value

    def __init__(self, classroomInstance: ClassroomInstance):
        self.name = classroomInstance.name
        self.capacity = classroomInstance.capacity
        self.uuid = secrets.token_urlsafe(Config.UUID_TOKEN_LENGTH)

        # self.facility = classroomInstance.facility

    def __repr__(self):
        return "<ClassroomInstanceDBEntry(brand='%s')>" % (
            self.name,
        )
