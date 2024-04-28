"""
I don't want to have the base table classes inherit from each other to avoid circular import hell.

Database queries are required to be passed
"""

from typing import List
from tables import *


class ChildTableHelpers:

    @staticmethod
    def getTeacherDBEntry(ChildDBEntry: ChildInstanceDBEntry, dbq=None) -> TeacherInstanceDBEntry:
        return ChildDBEntry.teacher


class TeacherTableHelpers:

    def __init__(self):
        pass

    @staticmethod
    def getChildInstanceEntries(teacherDataDict, dbq) -> List[ChildInstanceDBEntry]:
        childDBList = list()

        childIds = [int(x) for x in teacherDataDict.get("_childids", "").split(';') if x]

        for childId in childIds:
            childEntry: ChildInstanceDBEntry = dbq.childDB.filter_by(
                teacher_id = teacherDataDict.get("id"),
                id = childId
            ).first()
            childDBList.append(
                childEntry
            )
        return childDBList

    @staticmethod
    def getChildDataEntries(teacherDataDict, dbq) -> dict:
        childDBList = list()

        childIds = [int(x) for x in teacherDataDict.get("_childids", "").split(';') if x]

        for childId in childIds:
            childEntry: ChildInstanceDBEntry = dbq.childDB.filter_by(
                teacher_id = teacherDataDict.get("id"),
                id = childId
            ).first()
            childDBList.append(
                dbq.database.getTableContents(ChildInstanceDBEntry, childEntry, wantIdAsKey = False)
            )

        return childDBList

    @staticmethod
    def getFullname(teacherDataDict, dbq=None) -> str:
        return f"{teacherDataDict.get('firstname')} {teacherDataDict.get('lastname')}"


class ClassroomTableHelpers:

    def __init__(self):
        pass

    @staticmethod
    def getTeacherDBEntries(classroomDataDict, dbq) -> List[TeacherInstanceDBEntry]:
        teacherDBList = list()

        teacherIds = [int(x) for x in classroomDataDict.get("_teacherids", "").split(';') if x]

        for teacherId in teacherIds:
            teacherEntry: TeacherInstanceDBEntry = dbq.teacherDB.filter_by(
                classroom_id = classroomDataDict.get("id"),
                id = teacherId
            ).first()
            if teacherEntry:
                teacherDBList.append(teacherEntry)
        return teacherDBList

    @staticmethod
    def getTeacherDataEntries(classroomDataDict, dbq) -> dict:
        teacherDBList = list()

        teacherIds = [int(x) for x in classroomDataDict.get("_teacherids", "").split(';') if x]

        for teacherId in teacherIds:
            teacherEntry: TeacherInstanceDBEntry = dbq.teacherDB.filter_by(
                classroom_id = classroomDataDict.get("id"),
                id = teacherId
            ).first()
            teacherDBList.append(
                dbq.database.getTableContents(TeacherInstanceDBEntry, teacherEntry, wantIdAsKey = False)
            )
        return teacherDBList

    @staticmethod
    def getCurrentClassCapacity(classroomDataDict, dbq):
        """
        Get the amount of children that are in a classroom
        """
        classroomTeachers = ClassroomTableHelpers.getTeacherDBEntries(classroomDataDict, dbq)
        childCount = 0

        for classTeacher in classroomTeachers:
            # hack zzzz
            if isinstance(classTeacher, list):
                classTeacher = classTeacher[0]
            childCount += len(classTeacher.children)
        return childCount

    @staticmethod
    def getMaximumClassCapacity(classroomDataDict, dbq):
        currentCount = ClassroomTableHelpers.getCurrentClassCapacity(classroomDataDict, dbq)
        """
        if max capacity greater than 10 * num teachers, then num teachers should be considered
        """
        teacherCapacity = 10 * len(ClassroomTableHelpers.getTeacherDBEntries(classroomDataDict, dbq))
        roomCapacity = classroomDataDict.get('capacity', 0)
        # If our room capacity is less than our teacher capacity, then it becomes the lower bound
        if roomCapacity <= teacherCapacity:
            # 23 - 10 = 13
            return roomCapacity
        # But if our teacher capacity is less than our room capacity
        return teacherCapacity

    @staticmethod
    def getOpenClassSlots(classroomDataDict, dbq):
        # We need to consider constraints of the classrooms capacity
        return ClassroomTableHelpers.getMaximumClassCapacity(
            classroomDataDict, dbq
        ) - ClassroomTableHelpers.getCurrentClassCapacity(classroomDataDict, dbq)


class FacilityTableHelpers:
    @staticmethod
    def getClassroomDBEntries(facilityDataDict, dbq) -> List[ClassroomInstanceDBEntry]:
        classroomDBList = list()
        classroomIds = [int(x) for x in facilityDataDict.get("_classroomids", "").split(';') if x]

        for classroomId in classroomIds:
            classroomEntry: ClassroomInstanceDBEntry = dbq.classroomDB.filter_by(
                facility_id = facilityDataDict.get("id"),
                id = classroomId
            ).first()
            if classroomEntry:
                classroomDBList.append(classroomEntry)
        return classroomDBList
