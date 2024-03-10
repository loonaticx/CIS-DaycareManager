from typing import List

from sqlalchemy import Column, Integer, String

from tables.FacilityInstance import FacilityInstance

from sqlalchemy.orm import  Mapped,mapped_column

from base.DatabaseDriver import *


class FacilityInstanceDBEntry(Base):
    """
    Skeleton for a db entry in the "inventory" table.

    Will be added into the database upon init
    """

    __tablename__ = "facility"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String(64))
    # classrooms: Mapped[List["ClassroomInstanceDBEntry"]] = relationship(back_populates = "fac")
    classrooms = relationship("ClassroomInstanceDBEntry", back_populates = "facility")
    _classroomids = Column(db.String, default = '')

    @property
    def classroomid(self):
        return [int(x) for x in self._classroomids.split(';') if x]

    @classroomid.setter
    def classroomid(self, value):
        self._classroomids += '%s;' % value

    def __init__(self, facilityInstance: FacilityInstance):
        self.name = facilityInstance.name

    def __repr__(self):
        return "<InventoryItemDBEntry(brand='%s')>" % (
            self.name,
        )

if __name__ == "__main__":
    # from base.DatabaseManager import *
    # from config.Config import Config
    # testDB = DatabaseManager(Config)
    # testDB.initSession()
    testFacility = FacilityInstanceDBEntry(FacilityInstance("test"))
    testDB.generateEntry(testFacility)
    print(testFacility)
