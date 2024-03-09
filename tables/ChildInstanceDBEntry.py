from sqlalchemy import Column, Integer, String, ForeignKey

from base.DatabaseDriver import *
from tables.ClassroomInstance import ClassroomInstance
from tables.ChildInstance import ChildInstance
# from tables.FacilityInstanceDBEntry import FacilityInstanceDBEntry

from sqlalchemy.orm import declarative_base


class ChildInstanceDBEntry(Base):
    """
    Skeleton for a db entry in the "inventory" table.

    Will be added into the database upon init
    """

    __tablename__ = "child"

    id = Column(Integer, primary_key = True, autoincrement = True)
    firstname = Column(String(64))
    lastname = Column(String(64))

    classroom_id = Column(Integer, ForeignKey("classroom.id"))
    # classroom_name = Column(Integer, ForeignKey("classroom.name"))
    classroom = relationship('ClassroomInstanceDBEntry', foreign_keys = [classroom_id])

    teacher_id = Column(Integer, ForeignKey("teacher.id"))
    # teacher_fname = Column(Integer, ForeignKey("teacher.firstname"))
    # teacher_lname = Column(Integer, ForeignKey("teacher.lastname"))
    teacher = relationship('TeacherInstanceDBEntry', back_populates = "children", foreign_keys = [teacher_id])


    def __init__(self, childInstance: ChildInstance):
        self.firstname = childInstance.firstname
        self.lastname = childInstance.lastname
        self.age = childInstance.age


    def __repr__(self):
        return "<ChildInstanceDBEntry(brand='%s')>" % (
            self.name,
        )
