import copy

import flask
from dataclasses import dataclass

from auth.TokenGenerator import TokenGenerator
from base.RequestHelper import RequestHelper
from tables import *
from base.DatabaseDriver import *

from flask import Flask, request, abort, make_response
from flask_cors import CORS

app = Flask(__name__)
# https://stackoverflow.com/questions/20035101/why-does-my-javascript-code-receive-a-no-access-control-allow-origin
# -header-i
CORS(app)


# Zipped up to help with the traveling costs
@dataclass
class TableDatabaseQueries:
    database = Database
    facilityDB = Database.session.query(FacilityInstanceDBEntry)
    classroomDB = Database.session.query(ClassroomInstanceDBEntry)
    teacherDB = Database.session.query(TeacherInstanceDBEntry)
    childDB = Database.session.query(ChildInstanceDBEntry)

    def all(self):
        return [self.facilityDB, self.classroomDB, self.teacherDB, self.childDB]


DatabaseQueries = TableDatabaseQueries()

# Grab our tables
_facilityDB = DatabaseQueries.facilityDB
_classroomDB = DatabaseQueries.classroomDB
_teacherDB = DatabaseQueries.teacherDB
_childDB = DatabaseQueries.childDB

tokenGenerator = TokenGenerator()

from base.TableDataHelper import *


def jsonify(returnInfo):
    """
    Wrapper to remove specific entries from being
    put out in the API
    """
    def recursive(data):
        newData = {}
        if data:
            for k, v in data.items():
                try:
                    if "_badids" in k:
                        continue
                except:
                    pass
                if isinstance(v, dict):
                    v = recursive(v)
                newData[k] = v
        return newData

    newInfo = recursive(returnInfo)
    return flask.jsonify(newInfo)


"""
Auth Token Management
"""


# region
@app.route('/api/generate', methods = ['GET'], strict_slashes = False)
def generate_token():
    resp = make_response('Generated your token as a cookie.')
    resp.set_cookie('auth_token', tokenGenerator.generateToken(request.remote_addr).decode('utf-8'))
    return resp


def rejectNoToken():
    return abort(418, 'Invalid token. (Generate one with /api/generate)')


# endregion

"""
Facility Management
"""


# region

@app.route('/api/lookup/facility', methods = ['GET'], strict_slashes = False)
def all_facilities():
    # Fetch all entries
    facilityDict = Database.getTableContents(FacilityInstanceDBEntry)
    return jsonify(facilityDict)


@app.route('/api/lookup/<facilityId>', methods = ['GET', 'POST', 'PUT', 'DELETE'], strict_slashes = False)
def facility_info(facilityId):
    """
    :param facilityId: The UUID of the facility
    """
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()
    returnInfo = {}

    # Database ID or UUID?
    passedIdType = request.args.get('idType', "uuid")
    if passedIdType == "dbid":
        facilityId = int(facilityId)
    else:
        facilityId = int(getIDfromUUID(facilityId, FacilityInstanceDBEntry, _facilityDB))

    # if False: good if we want to add, bad if we are trying to get
    facilityDbEntry, facilityDataDict = getFacilityData(int(facilityId))
    if not facilityDataDict and request.method != "POST":
        abort(400, 'Invalid Facility ID')
    facilityIdOccupied = bool(facilityDbEntry or facilityDataDict)

    if request.method == "GET":
        facilityDbEntries: list[FacilityInstanceDBEntry] = _facilityDB.filter_by(id = facilityId).all()
        returnInfo = Database.getTableContents(FacilityInstanceDBEntry, facilityDbEntries)
    elif request.method == "POST":
        if facilityIdOccupied:
            # Return error, you cant create with the given ID
            abort(400, 'Facility ID Already occupied.')
        newFacilityEntry = FacilityInstanceDBEntry(FacilityInstance(**request.args))
        Database.generateEntry(newFacilityEntry)
        # Update the data dict with our new entry so that we can send a verified output
        facilityDataDict = Database.getTableContents(FacilityInstanceDBEntry)
        returnInfo = facilityDataDict.get(str(newFacilityEntry.uuid))

    elif request.method == "PUT":
        facilityDataDict = facilityDataDict.get(int(facilityId))
        facilityDbEntry, facilityDataDict = RequestHelper.doPut(request, facilityDbEntry, facilityDataDict)
        # Commit
        Database.session.commit()
        returnInfo = facilityDataDict

    elif request.method == 'DELETE':
        # Information Remove
        Database.session.delete(facilityDbEntry)
        Database.session.commit()
        returnInfo = "Facility Deleted"
    return jsonify(returnInfo)


def getFacilityData(facilityId: int | str):
    facilityDbEntry: FacilityInstanceDBEntry = _facilityDB.filter_by(
        id = facilityId,
    ).first()
    facilityDataDict = Database.getTableContents(FacilityInstanceDBEntry, [facilityDbEntry])
    return facilityDbEntry, facilityDataDict


def getIDfromUUID(uuid, dbEntry, database):
    dbEntry: dbEntry = database.filter_by(
        uuid = uuid,
    ).first()
    if not dbEntry:
        return -1
    return dbEntry.id


def getUUIDfromID(id, dbEntry, database):
    dbEntry: dbEntry = database.filter_by(
        id = id,
    ).first()
    if not dbEntry:
        return -1
    return dbEntry.uuid


# endregion


"""
Classroom Management
"""


# region

@app.route('/api/lookup/classrooms', methods = ['GET'], strict_slashes = False)
def all_classrooms():
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()
    # Fetch all entries
    classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
    return jsonify(classroomDict)


@app.route('/api/lookup/<facilityId>/', methods = ['GET'], strict_slashes = True)
def all_classrooms_in_facility(facilityId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()

    # Database ID or UUID?
    passedIdType = request.args.get('idType', "uuid")
    if passedIdType == "dbid":
        facilityId = int(facilityId)
        facilityUUID = getUUIDfromID(facilityId, FacilityInstanceDBEntry, _facilityDB)
    else:
        facilityUUID = facilityId
        facilityId = int(getIDfromUUID(facilityId, FacilityInstanceDBEntry, _facilityDB))

    if facilityId == -1:
        abort(400, 'Improper Facility ID given')

    prettyDict = {}
    classroomDataDict = {}
    # Fetch all entries
    classroomDbEntry: ClassroomInstanceDBEntry = _classroomDB.filter_by(
        facility_id = facilityId,
    ).all()
    if classroomDbEntry:
        classroomDataDict = Database.getTableContents(ClassroomInstanceDBEntry, classroomDbEntry)

    for classId, classData in classroomDataDict.items():
        className = classData.pop("name")
        classData["id"] = classId
        classData["parent"] = facilityUUID
        # [x for x in teacherDbEntry.children]
        # classData["teachers"] = Database.getTableContents(ClassroomInstanceDBEntry, [x for x in
        # classroomDbEntry.teachers])
        classData["teachers"] = ClassroomTableHelpers.getTeacherDataEntries(classData, DatabaseQueries)
        classData["current_capacity"] = ClassroomTableHelpers.getCurrentClassCapacity(classData, DatabaseQueries)
        classData["max_slots_possible"] = ClassroomTableHelpers.getMaximumClassCapacity(classData, DatabaseQueries)
        classData["remaining_slots"] = classData["max_slots_possible"] - ClassroomTableHelpers.getOpenClassSlots(
            classData, DatabaseQueries)
        prettyDict[className] = dict(**classData)

    # Grab metadata
    facilityDbEntry, facilityDataDict = getFacilityData(facilityId)

    outDict = {
        "metadata": {
            "facility_name": facilityDbEntry.name,
            "facility_uuid": facilityDbEntry.uuid,
            "method_src": "all_classrooms_in_facility",
        },
        "content": prettyDict,
    }

    return jsonify(outDict)


# metaTree = {
#     ["facilityName", "uuid"]: {
#         ["className", "uuid"]: {
#             ["teacherName", "uuid"]: {
#                 ["studentName", "uuid"]
#             }
#         }
#     }
# }


@app.route('/api/lookup/<facilityId>/<classroomId>', methods = ['GET', 'POST', 'PUT', 'DELETE'], strict_slashes = False)
def classroom_info(facilityId, classroomId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()
    returnInfo = {}

    # Database ID or UUID?
    passedIdType = request.args.get('idType', "uuid")
    if passedIdType == "dbid":
        facilityId = int(facilityId)
        classroomId = int(classroomId)
    else:
        facilityId = int(getIDfromUUID(facilityId, FacilityInstanceDBEntry, _facilityDB))
        classroomId = int(getIDfromUUID(classroomId, ClassroomInstanceDBEntry, _classroomDB))

    facilityDbEntry, facilityDataDict = getFacilityData(facilityId)
    if not facilityDataDict:
        abort(400, 'Invalid Facility ID')

    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    if request.method != "POST":
        if not classroomDataDict:
            abort(400, 'Improper Classroom ID given')
        else:
            classroomDataDict = classroomDataDict.get(int(classroomId))
            classroomDataDict["Teachers"] = {}

    # if False: good if we want to add, bad if we are trying to get
    classroomIdOccupied = classroomId in facilityDbEntry.classrooms

    classroomOutDict = {}
    if request.method == "GET":
        # So we only have one entry in the inbound dict
        teacherDBEntryDict, teacherDataDict = getTeacherData(classroomDbEntry)
        for teacherId, teacherEntry in teacherDataDict.items():
            # if teacherEntry.classroom_id == classroomId:
            classroomDataDict["Teachers"][teacherId] = dict(**teacherEntry)

        returnInfo = classroomDataDict

    elif request.method == "POST":
        # TODO: reject if input name already exists in db
        if classroomIdOccupied:
            # Return error, you cant create with the given ID
            abort(400, 'Classroom ID Already occupied.')
        newClassroomEntry = ClassroomInstanceDBEntry(ClassroomInstance(**request.args))
        newClassroomEntry.facility_id = facilityId
        Database.generateEntry(newClassroomEntry)
        # Update the data dict with our new entry so that we can send a verified output
        classroomDataDict = Database.getTableContents(ClassroomInstanceDBEntry)
        returnInfo = classroomDataDict.get(int(newClassroomEntry.id))

    elif request.method == "PUT":
        classroomDbEntry, classroomDataDict = RequestHelper.doPut(request, classroomDbEntry, classroomDataDict)
        # Commit
        Database.session.commit()

        returnInfo = classroomDataDict

    elif request.method == 'DELETE':
        # Information Remove
        Database.session.delete(classroomDbEntry)
        Database.session.commit()
        returnInfo = "Classroom Deleted"

    outDict = {
        "metadata": {
            "facility_name": facilityDbEntry.name,
            "facility_uuid": facilityDbEntry.uuid,
            "classroom_name": classroomDbEntry.name,
            # classroom_uuid is already content.uuid
            "method_src": "classroom_info",
            "occupied_slots": ClassroomTableHelpers.getCurrentClassCapacity(classroomDataDict, DatabaseQueries),
            "unoccupied_slots": ClassroomTableHelpers.getOpenClassSlots(classroomDataDict, DatabaseQueries),
        },
        "content": returnInfo,
    }

    return jsonify(outDict)


def getClassroomData(facilityId: int | str, classroomId: int | str):
    """
    :param int|str facilityId: internal id (NOT uuid)
    :param int|str classroomId: internal id (NOT uuid)

    """
    classroomDbEntry: ClassroomInstanceDBEntry = _classroomDB.filter_by(
        facility_id = facilityId,
        id = classroomId
    ).first()
    classroomDataDict = Database.getTableContents(ClassroomInstanceDBEntry, [classroomDbEntry])
    return classroomDbEntry, classroomDataDict


# endregion


"""
Teacher Management
"""


# region

@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>', methods = ['GET', 'POST', 'DELETE', 'PUT'],
           strict_slashes = False)
def teacher_info(facilityId, classroomId, teacherId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()
    returnInfo = {}

    # Database ID or UUID?
    passedIdType = request.args.get('idType', "uuid")
    if passedIdType == "dbid":
        facilityId = int(facilityId)
        classroomId = int(classroomId)
        teacherId = int(teacherId)
    else:
        facilityId = int(getIDfromUUID(facilityId, FacilityInstanceDBEntry, _facilityDB))
        classroomId = int(getIDfromUUID(classroomId, ClassroomInstanceDBEntry, _classroomDB))
        teacherId = int(getIDfromUUID(teacherId, TeacherInstanceDBEntry, _teacherDB))

    facilityDbEntry, facilityDataDict = getFacilityData(facilityId)
    if not facilityDataDict:
        abort(400, 'Invalid Facility ID')

    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    if not classroomDataDict:
        abort(400, 'Invalid Classroom ID')

    # if False: good if we want to add, bad if we are trying to get
    teacherIdOccupied = teacherId in classroomDbEntry.teacherids

    teacherDbEntry, teacherDataDict = getTeacherData(classroomDbEntry)
    teacherDbEntry = teacherDbEntry.get(teacherId)
    teacherDataDict = teacherDataDict.get(teacherId)

    if request.method == "GET":
        returnInfo = teacherDataDict

    elif request.method == "POST":
        if teacherIdOccupied:
            # Return error, you cant create a teacher with the given ID
            abort(400, 'Teacher ID already occupied.')
        newTeacherEntry = TeacherInstanceDBEntry(TeacherInstance(**request.args))
        newTeacherEntry.classroom_id = classroomId
        Database.generateEntry(newTeacherEntry)
        # CAREFUL!

        classroomDbEntry.teacherids = newTeacherEntry.id
        Database.session.commit()

        # Update the data dict with our new entry so that we can send a verified output
        teacherDataDict = Database.getTableContents(TeacherInstanceDBEntry)
        teacherDbEntry = newTeacherEntry
        returnInfo = teacherDataDict.get(int(newTeacherEntry.id))

    elif request.method == "PUT":
        # teacherDataDict = teacherDataDict.get(int(teacherId))
        teacherDbEntry, teacherDataDict = RequestHelper.doPut(request, teacherDbEntry, teacherDataDict)
        # Commit
        Database.session.commit()
        returnInfo = teacherDataDict

    elif request.method == 'DELETE':
        # Information Remove
        Database.session.delete(teacherDbEntry)
        Database.session.commit()
        returnInfo = "Teacher Deleted"

    outDict = {
        "metadata": {
            "facility_name": facilityDbEntry.name,
            "facility_uuid": facilityDbEntry.uuid,
            "classroom_uuid": classroomDbEntry.uuid,
            "classroom_name": classroomDbEntry.name,
            "method_src": "teacher_info",
            "child_occupied_slots": len(teacherDbEntry.children),
            "classroom_occupied_slots": ClassroomTableHelpers.getCurrentClassCapacity(
                classroomDataDict, DatabaseQueries
            ),
            "classroom_unoccupied_slots": ClassroomTableHelpers.getOpenClassSlots(classroomDataDict, DatabaseQueries),

        },
        "content": returnInfo,
    }

    return jsonify(outDict)


def getTeacherData(classroomDbEntry):
    teacherDataDict = dict()
    teacherDBEntryDict = dict()
    for teacherId in classroomDbEntry.teacherids:
        teacherEntry: TeacherInstanceDBEntry = _teacherDB.filter_by(
            classroom_id = classroomDbEntry.id,
            id = teacherId
        ).first()
        if not teacherEntry:
            classroomDbEntry.badids = teacherId
            continue
        tData = Database.getTableContents(TeacherInstanceDBEntry, [teacherEntry])
        # We have this weird nest to deal with
        for tId, tContent in tData.items():
            teacherDataDict[teacherId] = tContent
        teacherDataDict[teacherId]["Children"] = {}

        # Multiple kids can be hereaaa
        childDbEntry: ChildInstanceDBEntry = _childDB.filter_by(
            classroom_id = classroomDbEntry.id,
            teacher_id = teacherId
        ).all()
        childDataDict = Database.getTableContents(ChildInstanceDBEntry, childDbEntry)
        for childId, childEntry in childDataDict.items():
            if int(childId) in teacherEntry.childids:
                teacherDataDict[teacherId]["Children"][childId] = dict(**childEntry)
        teacherDBEntryDict[teacherId] = teacherEntry

    # Cleanup bad ids
    for badid in classroomDbEntry.badids:
        classroomDbEntry.teacherids = badid

    return teacherDBEntryDict, teacherDataDict


# endregion

"""
Child Management
"""


# region

@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>/<childId>', methods = ['GET', 'POST', 'DELETE', 'PUT'],
           strict_slashes = False)
def child_info(facilityId, classroomId, teacherId, childId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()
    returnInfo = {}

    # Database ID or UUID?
    passedIdType = request.args.get('idType', "uuid")
    if passedIdType == "dbid":
        facilityId = int(facilityId)
        classroomId = int(classroomId)
        teacherId = int(teacherId)
        childId = int(childId)
    else:
        facilityId = int(getIDfromUUID(facilityId, FacilityInstanceDBEntry, _facilityDB))
        classroomId = int(getIDfromUUID(classroomId, ClassroomInstanceDBEntry, _classroomDB))
        teacherId = int(getIDfromUUID(teacherId, TeacherInstanceDBEntry, _teacherDB))
        childId = int(getIDfromUUID(childId, ChildInstanceDBEntry, _childDB))

    facilityDbEntry, facilityDataDict = getFacilityData(facilityId)
    if not facilityDataDict:
        abort(400, 'Invalid facility ID.')

    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    if not classroomDataDict:
        abort(400, 'Invalid classroom ID.')
    teacherDbEntry, allTeacherDataDict = getTeacherData(classroomDbEntry)
    teacherDbEntry = teacherDbEntry.get(teacherId)
    teacherDataDict = allTeacherDataDict.pop(teacherId)

    currentSpots = classroomDataDict[classroomId]['capacity']
    currentOccupied = len(teacherDataDict["Children"])
    for _, otherTeachers in allTeacherDataDict.items():
        currentOccupied += len(otherTeachers["Children"])

    childDbEntry, childDataDict = getChildData(teacherDbEntry)
    if not childDbEntry and request.method != "POST":
        abort(400, 'Invalid Child ID')
    childDbEntry = childDbEntry.get(childId)
    childDataDict = childDataDict.get(childId)

    # if False: good if we want to add, bad if we are trying to GET
    childIdOccupied = childId in teacherDbEntry.childids

    if request.method == "GET":
        returnInfo = childDataDict

    elif request.method == "POST":
        if childIdOccupied:
            # Return error, you cant create a child with the given ID
            abort(400, 'Child ID Already occupied.')
        if currentSpots - currentOccupiedWithClassroom <= 0:
            abort(400, 'Classroom is full.')

        if len(teacherDataDict["Children"]) >= 10:
            abort(400, 'Too many children for this teacher!')
        newChildEntry = ChildInstanceDBEntry(ChildInstance(**request.args))
        newChildEntry.teacher_id = teacherId
        newChildEntry.classroom_id = classroomId
        Database.generateEntry(newChildEntry)

        teacherDbEntry.childids = newChildEntry.id
        # Update the data dict with our new entry so that we can send a verified output
        childDataDict = Database.getTableContents(ChildInstanceDBEntry)
        returnInfo = childDataDict.get(int(newChildEntry.id))

    elif request.method == "PUT":
        childDataDict = childDataDict.get(int(childId))
        childDbEntry, childDataDict = RequestHelper.doPut(request, childDbEntry, childDataDict)
        # Commit
        Database.session.commit()
        returnInfo = childDataDict

    elif request.method == 'DELETE':
        # Information Remove
        Database.session.delete(childDbEntry)
        Database.session.commit()
        # Todo: Detach from teacher
        # KILL CHILD
        returnInfo = "Child Deleted"

    child_metadata = dict()
    if childDbEntry:
        child_metadata = {
            "child_name": f"{childDbEntry.firstname} {childDbEntry.lastname}",
            "child_id": childDbEntry.uuid,
        }

    outDict = {
        "metadata": {
            "facility_name": facilityDbEntry.name,
            "facility_uuid": facilityDbEntry.uuid,
            "classroom_name": classroomDbEntry.name,
            "classroom_uuid": classroomDbEntry.uuid,
            "teacher_name": f"{teacherDbEntry.firstname} {teacherDbEntry.lastname}",
            "teacher_uuid": teacherDbEntry.uuid,
            **child_metadata

        },
        "content": returnInfo,
    }

    return jsonify(outDict)


@app.route('/api/tree', methods = ['GET'],
           strict_slashes = False)
def tree():
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        return rejectNoToken()
    level = int(request.args.get('level', "1"))

    facilityDatas = Database.getTableContents(FacilityInstanceDBEntry, wantIdAsKey = False)
    if not isinstance(facilityDatas, list):
        facilityDatas = [facilityDatas]
    data = dict()
    for facilityDataDict in facilityDatas:
        classDataEntries = dict()
        innerFacilityDict = data[facilityDataDict.get("name")] = dict()
        if level > 1:
            for classDBEntry in FacilityTableHelpers.getClassroomDBEntries(facilityDataDict, DatabaseQueries):
                classroomDataDict = Database.getTableContents(
                    ClassroomInstanceDBEntry, [classDBEntry], wantIdAsKey = False
                )
                teacherDataEntries = []
                innerClassDict = classDataEntries[classroomDataDict.get("name")] = dict()
                if level > 2:
                    for teacherDbEntry in ClassroomTableHelpers.getTeacherDBEntries(classroomDataDict, DatabaseQueries):
                        teacherDataDict = Database.getTableContents(
                            TeacherInstanceDBEntry, [teacherDbEntry], wantIdAsKey = False
                        )
                        teacherDataEntries.append({
                            "name": TeacherTableHelpers.getFullname(teacherDataDict),
                            "uuid": teacherDataDict.get("uuid")
                        })
                    # classDataEntries[classroomDataDict] = teacherDataEntries
                    innerClassDict["teachers"] = teacherDataEntries
                innerClassDict["uuid"] = classroomDataDict.get("uuid")
            innerFacilityDict["classrooms"] = classDataEntries
        innerFacilityDict["uuid"] = facilityDataDict.get("uuid")

    DirectoryTree = [
        {
            "FacilityNameA": [
                {
                    "ClassroomNameA": [
                        "TeacherNameA", "TeacherNameB"
                    ]
                }
            ]
        }
    ]

    # Give us a tree
    test = {
        "Facilities": [
            {
                "FacilityNameA": [
                    {
                        "ClassroomNameA": [
                            "TeacherNameA", "TeacherNameB"
                        ]
                    }
                ]
            }

        ]

    }

    outDict = data

    return jsonify(outDict)


def getChildData(teacherDbEntry):
    childDataDict = dict()
    childDBEntryDict = dict()
    for childId in teacherDbEntry.childids:
        childDbEntry: ChildInstanceDBEntry = _childDB.filter_by(
            teacher_id = teacherDbEntry.id,
            id = childId
        ).first()
        cData = Database.getTableContents(ChildInstanceDBEntry, [childDbEntry])
        # We have this weird nest to deal with
        if cData:
            for cId, cContent in cData.items():
                childDataDict[childId] = cContent

            childDBEntryDict[childId] = childDbEntry
    return childDBEntryDict, childDataDict


# endregion

app.run(Config.FLASK_HOST, debug = Config.FLASK_WANT_DEBUG)
