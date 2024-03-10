
from tables import *
from base.DatabaseDriver import *

from flask import Flask, jsonify, request

app = Flask(__name__)


# Grab our tables
_facilityDB = Database.session.query(FacilityInstanceDBEntry)
_classroomDB = Database.session.query(ClassroomInstanceDBEntry)
_teacherDB = Database.session.query(TeacherInstanceDBEntry)

#
# @app.route('/api/lookup/facility', methods = ['GET'], strict_slashes = False)
# def all_tires():
#     # Fetch all entries
#     tireDict = Database.getTableContents(FacilityInstanceDBEntry)
#     return jsonify(tireDict)

@app.route('/api/lookup/facility', methods = ['GET'], strict_slashes = False)
def all_facilities():
    # Fetch all entries
    facilityDict = Database.getTableContents(FacilityInstanceDBEntry)
    return jsonify(facilityDict)




@app.route('/api/lookup/facility/<facilityId>', methods = ['GET'], strict_slashes = False)
def facility_info(facilityId):
    # Fetch all entries
    # classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
    returnInfo = []
    classroomDbEntries: list[ClassroomInstanceDBEntry] = _classroomDB.filter_by(facility_id = facilityId).all()
    returnInfo = Database.getTableContents(ClassroomInstanceDBEntry, classroomDbEntries)

    print(f"a = {returnInfo}")
    return jsonify(returnInfo)

@app.route('/api/lookup/classrooms', methods = ['GET'], strict_slashes = False)
def all_classrooms():
    # Fetch all entries
    classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
    return jsonify(classroomDict)


@app.route('/api/lookup/<facilityId>/<classroomId>', methods = ['GET'], strict_slashes = False)
def classroom_info(facilityId, classroomId):
    returnInfo = {}
    if request.method == "GET":
        # classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
        classroomDbEntry: ClassroomInstanceDBEntry = _classroomDB.filter_by(
            facility_id = facilityId, id = classroomId
        ).first()
        classroomDict = Database.getTableContents(type(classroomDbEntry), [classroomDbEntry])
        # Get more information

        # classroomDict["Teachers"] = dict()

        teacherDataDict = dict()
        for teacherId in classroomDbEntry.teacherids:
            teacherEntry: TeacherInstanceDBEntry = _teacherDB.filter_by(
                classroom_id=classroomDbEntry.id,
                id=teacherId
            ).first()
            # teacherDataDict[teacherId] = Database.getTableContents(TeacherInstanceDBEntry, [teacherEntry])
            # classroomDict["Teachers"].update(Database.getTableContents(TeacherInstanceDBEntry, [teacherEntry]))
        # classroomDict["Teachers"] = teacherDataDict
        print(classroomDict)
        returnInfo = classroomDict

    return jsonify(returnInfo)


@app.route('/api/lookup/<facilityId>/<classroomId>/<teacherId>', methods = ['GET'], strict_slashes = False)
def teacher_info(facilityId, classroomId, teacherId):
    # classroomDict = Database.getTableContents(ClassroomInstanceDBEntry)
    classinfo = classroom_info(facilityId, classroomId)
    classroomDbEntry: TeacherInstanceDBEntry = _teacherDB.filter_by(
        classroom_id = classroomId, id = classroomId,
    ).first()
    classroomDict = Database.getTableContents(type(classroomDbEntry), [classroomDbEntry])
    # Get more information

    # classroomDict["Teachers"] = dict()

    # get a list of teacher uuids, can be used to cross check.

    teacherDataDict = dict()
    for teacherId in classroomDbEntry.teacherids:
        teacherEntry: TeacherInstanceDBEntry = _teacherDB.filter_by(
            classroom_id=classroomDbEntry.id,
            id=teacherId
        ).first()
        # teacherDataDict[teacherId] = Database.getTableContents(TeacherInstanceDBEntry, [teacherEntry])
        # classroomDict["Teachers"].update(Database.getTableContents(TeacherInstanceDBEntry, [teacherEntry]))
    # classroomDict["Teachers"] = teacherDataDict
    print(classroomDict)

    return jsonify(classroomDict)

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
