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
    facilityIdOccupied = bool(facilityDbEntry or facilityDataDict)

    if request.method == "GET":
        facilityDbEntries: list[FacilityInstanceDBEntry] = _facilityDB.filter_by(id = facilityId).all()
        returnInfo = Database.getTableContents(FacilityInstanceDBEntry, facilityDbEntries)
    elif request.method == "POST":
        if facilityIdOccupied:
            # Return error, you cant create with the given ID
            return
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
        returnInfo = "Item Deleted"
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

    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    if not classroomDataDict:
        abort(400, 'Invalid Classroom ID')
    # classroomDbEntry = classroomDbEntry.get(classroomId)
    classroomDataDict = classroomDataDict.get(classroomId)

    # if False: good if we want to add, bad if we are trying to get
    classroomIdOccupied = classroomId in facilityDbEntry.classrooms

    classroomOutDict = {}
    classroomDataDict["Teachers"] = {}
    if request.method == "GET":
        # So we only have one entry in the inbound dict
        print(f"a {classroomDataDict}")
        teacherDBEntryDict, teacherDataDict = getTeacherData(classroomDbEntry)
        for teacherId, teacherEntry in teacherDataDict.items():
            classroomDataDict["Teachers"][teacherId] = dict(**teacherEntry)
        # classroomDict[-1] = {}
        # classroomOutDict["Teachers"] = dict()

        returnInfo = classroomDataDict

    elif request.method == "POST":
        if classroomIdOccupied:
            # Return error, you cant create with the given ID
            return
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
        returnInfo = "Item Deleted"

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
        # classroomDict["Teachers"].update(Database.getTableContents(TeacherInstanceDBEntry, [teacherEntry]))
        teacherDataDict[teacherId]["Children"] = {}

        # Multiple kids can be hereaaa
        childDbEntry: ChildInstanceDBEntry = _childDB.filter_by(
            classroom_id = classroomDbEntry.id,
            teacher_id = teacherId
        ).all()
        childDataDict = Database.getTableContents(ChildInstanceDBEntry, childDbEntry)
        for childId, childEntry in childDataDict.items():
            # childEntry.pop("_childids")
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
    facilityDataDict = Database.getTableContents(type(facilityDbEntry), [facilityDbEntry])
    return facilityDbEntry, facilityDataDict



@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>', methods = ['GET', 'POST', 'DELETE', 'PUT'], strict_slashes = False)
def teacher_info(facilityId, classroomId, teacherId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    returnInfo = {}
    # classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
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
            return
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
        Database.session.delete(classroomDbEntry)
        Database.session.commit()
        returnInfo = "Item Deleted"

    return jsonify(returnInfo)


@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>/<childId>', methods = ['GET', 'POST', 'DELETE', 'PUT'],
           strict_slashes = False)
def child_info(facilityId, classroomId, teacherId, childId):
    if not tokenGenerator.isTokenValid(request.cookies.get('auth_token')):
        abort(400, 'Invalid token. (Generate one with /api/generate)')
    returnInfo = {}
    teacherId = int(teacherId)
    childId = int(childId)

    classroomDbEntry, classroomDataDict = getClassroomData(facilityId, classroomId)
    teacherDbEntry, teacherDataDict = getTeacherData(classroomDbEntry)
    teacherDbEntry = teacherDbEntry.get(teacherId)
    teacherDataDict = teacherDataDict.get(teacherId)

    childDbEntry, childDataDict = getChildData(teacherDbEntry)
    childDbEntry = childDbEntry.get(childId)
    childDataDict = childDataDict.get(childId)

    # if False: good if we want to add, bad if we are trying to GET
    childIdOccupied = childId in teacherDbEntry.childids

    if request.method == "GET":
        returnInfo = childDataDict

    elif request.method == "POST":
        if childIdOccupied:
            # Return error, you cant create a teacher with the given ID
            return
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
        # KILL CHILD
        returnInfo = "Child Deleted"

    return jsonify(returnInfo)


#
# @app.route('/api/inventory/<tireId>', methods = ['POST', 'PUT', 'GET', 'DELETE'])
# def manage_tire(tireId):
#     returnInfo = {}
#     # Grab the dict that has all the entries for this table (InventoryItemDBEntry)
#     registeredTiresDict = database.getTableContents(InventoryItemDBEntry)
#
#     tireId = int(tireId)
#
#     tireDataDict: dict = registeredTiresDict.get(tireId)
#     # Get DB entry by querying id
#     tireDbEntry: InventoryItemDBEntry = _tireDB.filter_by(id = tireId).first()
#
#     if request.method == 'GET':
#         # Information Get
#         returnInfo = registeredTiresDict.get(tireId)
#
#     elif request.method == 'PUT':
#         # Information Modify
#         def correctValType(entry_attr, _val_):
#             """
#             Attempts to correct input to the data type associated with the attribute in the database.
#             """
#             if isinstance(entry_attr, int) and _val_.isdigit():
#                 _val_ = int(_val_)
#             if isinstance(entry_attr, str):
#                 _val_ = str(_val_)
#             return _val_
#
#         # requested_arg here should be attributes/columns that were given to us from the input
#         # & _val of course is the data we want to set the attribute to.
#         for requested_arg, _val in request.args.items():
#             if hasattr(tireDbEntry, requested_arg):
#                 val = correctValType(getattr(tireDbEntry, requested_arg), _val)
#                 tireDataDict[requested_arg] = val
#                 tireDbEntry.requested_arg = val
#
#         # Commit
#         database.session.commit()
#         returnInfo = tireDataDict
#
#     elif request.method == 'POST':
#         # Information Add
#         newTireEntry = InventoryItemDBEntry(InventoryItem(**request.args))
#         database.generateEntry(newTireEntry)
#         # Update the data dict with our new entry so that we can send a verified output
#         tireDataDict = database.getTableContents(InventoryItemDBEntry)
#         returnInfo = tireDataDict.get(int(newTireEntry.id))
#
#     elif request.method == 'DELETE':
#         # Information Remove
#         database.session.delete(tireDbEntry)
#         database.session.commit()
#         returnInfo = "Item Deleted"
#
#     return jsonify(returnInfo)


app.run(Config.FLASK_HOST, debug = Config.FLASK_WANT_DEBUG)
