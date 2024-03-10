from auth.TokenGenerator import TokenGenerator
from base.RequestHelper import RequestHelper
from tables import *
from base.DatabaseDriver import *

from flask import Flask, jsonify, request, abort, make_response

app = Flask(__name__)

# Grab our tables
_facilityDB = Database.session.query(FacilityInstanceDBEntry)
_classroomDB = Database.session.query(ClassroomInstanceDBEntry)
_teacherDB = Database.session.query(TeacherInstanceDBEntry)
_childDB = Database.session.query(ChildInstanceDBEntry)

tokenGenerator = TokenGenerator()


@app.route('/api/generate', methods = ['GET'], strict_slashes = False)
def generate_token():
    resp = make_response('Generated your token as a cookie.')
    resp.set_cookie('auth_token', tokenGenerator.generateToken(request.remote_addr).decode('utf-8'))
    return resp


@app.route('/api/lookup/facility', methods = ['GET'], strict_slashes = False)
def all_facilities():
    # Fetch all entries
    facilityDict = Database.getTableContents(FacilityInstanceDBEntry)
    return jsonify(facilityDict)


@app.route('/api/lookup/<facilityId>', methods = ['GET', 'POST', 'PUT', 'DELETE'], strict_slashes = False)
def facility_info(facilityId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    returnInfo = {}

    # if False: good if we want to add, bad if we are trying to get
    facilityDbEntry, facilityDataDict = getFacilityData(facilityId)
    if not facilityDataDict:
        abort(400, 'Invalid Facility ID')
    facilityIdOccupied = bool(facilityDbEntry or facilityDataDict)

    if request.method == "GET":
        facilityDbEntries: list[FacilityInstanceDBEntry] = _facilityDB.filter_by(id = facilityId).all()
        returnInfo = Database.getTableContents(FacilityInstanceDBEntry, facilityDbEntries)
    elif request.method == "POST":
        if facilityIdOccupied:
            # Return error, you cant create with the given ID
            abort(400, 'ID Already occupied.')
        newFacilityEntry = FacilityInstanceDBEntry(FacilityInstance(**request.args))
        Database.generateEntry(newFacilityEntry)
        # Update the data dict with our new entry so that we can send a verified output
        facilityDataDict = Database.getTableContents(FacilityInstanceDBEntry)
        returnInfo = facilityDataDict.get(int(newFacilityEntry.id))

    elif request.method == "PUT":
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


@app.route('/api/lookup/classrooms', methods = ['GET'], strict_slashes = False)
def all_classrooms():
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    # Fetch all entries
    classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
    return jsonify(classroomDict)


@app.route('/api/lookup/<facilityId>/', methods = ['GET'], strict_slashes = True)
def all_classrooms_in_facility(facilityId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    prettyDict = {}
    # Fetch all entries
    classroomDbEntry: ClassroomInstanceDBEntry = _classroomDB.filter_by(
        facility_id = facilityId,
    ).all()
    classroomDataDict = Database.getTableContents(ClassroomInstanceDBEntry, classroomDbEntry)

    for classId, classData in classroomDataDict.items():
        className = classData.pop("name")
        classData["id"] = classId
        prettyDict[className] = dict(**classData)

    return jsonify(prettyDict)


@app.route('/api/lookup/<facilityId>/<classroomId>', methods = ['GET', 'POST', 'PUT', 'DELETE'], strict_slashes = False)
def classroom_info(facilityId, classroomId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    returnInfo = {}
    facilityId = int(facilityId)
    classroomId = int(classroomId)

    facilityDbEntry, facilityDataDict = getFacilityData(facilityId)
    if not facilityDataDict:
        abort(400, 'Invalid Facility ID')

    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    if not classroomDataDict:
        abort(400, 'Invalid Classroom ID')
    classroomDataDict = classroomDataDict.get(classroomId)

    # if False: good if we want to add, bad if we are trying to get
    classroomIdOccupied = classroomId in facilityDbEntry.classrooms

    classroomOutDict = {}
    classroomDataDict["Teachers"] = {}
    if request.method == "GET":
        # So we only have one entry in the inbound dict
        teacherDBEntryDict, teacherDataDict = getTeacherData(classroomDbEntry)
        for teacherId, teacherEntry in teacherDataDict.items():
            classroomDataDict["Teachers"][teacherId] = dict(**teacherEntry)

        returnInfo = classroomDataDict

    elif request.method == "POST":
        if classroomIdOccupied:
            # Return error, you cant create with the given ID
            abort(400, 'ID Already occupied.')
        newClassroomEntry = ClassroomInstanceDBEntry(ClassroomInstance(**request.args))
        Database.generateEntry(newClassroomEntry)
        newClassroomEntry.facility_id = facilityId
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

    return jsonify(returnInfo)


def getTeacherData(classroomDbEntry):
    teacherDataDict = dict()
    teacherDBEntryDict = dict()
    for teacherId in classroomDbEntry.teacherids:
        teacherEntry: TeacherInstanceDBEntry = _teacherDB.filter_by(
            classroom_id = classroomDbEntry.id,
            id = teacherId
        ).first()
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
    return teacherDBEntryDict, teacherDataDict


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


def getClassroomData(facilityId, classroomId):
    classroomDbEntry: ClassroomInstanceDBEntry = _classroomDB.filter_by(
        facility_id = facilityId,
        id = classroomId
    ).first()
    classroomDataDict = Database.getTableContents(ClassroomInstanceDBEntry, [classroomDbEntry])
    return classroomDbEntry, classroomDataDict


def getFacilityData(facilityId):
    facilityDbEntry: FacilityInstanceDBEntry = _facilityDB.filter_by(
        id = facilityId,
    ).first()
    facilityDataDict = Database.getTableContents(FacilityInstanceDBEntry, [facilityDbEntry])
    return facilityDbEntry, facilityDataDict


@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>', methods = ['GET', 'POST', 'DELETE', 'PUT'],
           strict_slashes = False)
def teacher_info(facilityId, classroomId, teacherId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    returnInfo = {}
    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    if not classroomDataDict:
        abort(400, 'Invalid Classroom ID')
    teacherId = int(teacherId)
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
            abort(400, 'ID already occupied.')
        newTeacherEntry = TeacherInstanceDBEntry(TeacherInstance(**request.args))
        Database.generateEntry(newTeacherEntry)
        newTeacherEntry.classroom_id = classroomId
        # Update the data dict with our new entry so that we can send a verified output
        teacherDataDict = Database.getTableContents(TeacherInstanceDBEntry)
        returnInfo = teacherDataDict.get(int(newTeacherEntry.id))

    elif request.method == "PUT":
        teacherDbEntry, teacherDataDict = RequestHelper.doPut(request, teacherDbEntry, teacherDataDict)
        # Commit
        Database.session.commit()
        returnInfo = teacherDataDict

    elif request.method == 'DELETE':
        # Information Remove
        Database.session.delete(teacherDbEntry)
        Database.session.commit()
        returnInfo = "Teacher Deleted"

    return jsonify(returnInfo)


@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>/<childId>', methods = ['GET', 'POST', 'DELETE', 'PUT'],
           strict_slashes = False)
def child_info(facilityId, classroomId, teacherId, childId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    returnInfo = {}
    classroomId = int(classroomId)
    teacherId = int(teacherId)
    childId = int(childId)

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
    if not childDbEntry:
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
            abort(400, 'ID Already occupied.')
        if currentSpots - currentOccupied <= 0:
            abort(400, 'Classroom is full.')

        if len(teacherDataDict["Children"]) >= 10:
            abort(400, 'Too many children for this teacher!')
        newChildEntry = ChildInstanceDBEntry(ChildInstance(**request.args))
        Database.generateEntry(newChildEntry)
        newChildEntry.teacher_id = teacherId
        # Update the data dict with our new entry so that we can send a verified output
        childDataDict = Database.getTableContents(ChildInstanceDBEntry)
        returnInfo = childDataDict.get(int(newChildEntry.id))

    elif request.method == "PUT":
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

    return jsonify(returnInfo)


app.run(Config.FLASK_HOST, debug = Config.FLASK_WANT_DEBUG)
