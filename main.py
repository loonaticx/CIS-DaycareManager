"""
This homework requires you to have a remote MySQL database setup.
For this assignment, we will create an inventory management system for a tire store.
Create a table in your existing database named inventory. In this table you need at least
the following columns: id, brand, model, loadrating, speedrating, type, stock. You may
add additional columns if you like

"""
from base.DatabaseManager import DatabaseManager
from tables.InventoryItem import InventoryItem
from tables.InventoryItemDB import InventoryItemDBEntry
from config.Config import Config
from flask import Flask, jsonify, request

app = Flask(__name__)

# Generate our DB
database = DatabaseManager(Config)
database.initSession()

# Grab our table
_tireDB = database.session.query(InventoryItemDBEntry)


@app.route('/api/inventory', methods = ['GET'], strict_slashes = False)
def all_tires():
    # Fetch all entries
    tireDict = database.getTableContents(InventoryItemDBEntry)
    return jsonify(tireDict)


@app.route('/api/inventory/<tireId>', methods = ['POST', 'PUT', 'GET', 'DELETE'])
def manage_tire(tireId):
    returnInfo = {}
    # Grab the dict that has all the entries for this table (InventoryItemDBEntry)
    registeredTiresDict = database.getTableContents(InventoryItemDBEntry)

    tireId = int(tireId)

    tireDataDict: dict = registeredTiresDict.get(tireId)
    # Get DB entry by querying id
    tireDbEntry: InventoryItemDBEntry = _tireDB.filter_by(id = tireId).first()

    if request.method == 'GET':
        # Information Get
        returnInfo = registeredTiresDict.get(tireId)

    elif request.method == 'PUT':
        # Information Modify
        def correctValType(entry_attr, _val_):
            """
            Attempts to correct input to the data type associated with the attribute in the database.
            """
            if isinstance(entry_attr, int) and _val_.isdigit():
                _val_ = int(_val_)
            if isinstance(entry_attr, str):
                _val_ = str(_val_)
            return _val_

        # requested_arg here should be attributes/columns that were given to us from the input
        # & _val of course is the data we want to set the attribute to.
        for requested_arg, _val in request.args.items():
            if hasattr(tireDbEntry, requested_arg):
                val = correctValType(getattr(tireDbEntry, requested_arg), _val)
                tireDataDict[requested_arg] = val
                tireDbEntry.requested_arg = val

        # Commit
        database.session.commit()
        returnInfo = tireDataDict

    elif request.method == 'POST':
        # Information Add
        newTireEntry = InventoryItemDBEntry(InventoryItem(**request.args))
        database.generateEntry(newTireEntry)
        # Update the data dict with our new entry so that we can send a verified output
        tireDataDict = database.getTableContents(InventoryItemDBEntry)
        returnInfo = tireDataDict.get(int(newTireEntry.id))

    elif request.method == 'DELETE':
        # Information Remove
        database.session.delete(tireDbEntry)
        database.session.commit()
        returnInfo = "Item Deleted"

    return jsonify(returnInfo)


app.run(Config.FLASK_HOST, debug = Config.FLASK_WANT_DEBUG)
