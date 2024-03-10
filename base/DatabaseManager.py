"""
DatabaseManager is the kickstart engine for connecting and working with the database.
"""

import sqlalchemy as db

from sqlalchemy import create_engine, update
from sqlalchemy.engine import URL
from sqlalchemy.sql import text

from base.ConnectionType import ConnectionType
import sys
from sqlalchemy.orm import sessionmaker, declarative_base

global initialized
initialized = False


class DatabaseManager:

    def __init__(self, config):
        global initialized
        if initialized:
            raise Exception("Can't initialize DatabaseManager more than once!")
        self._config = config
        self.session = None
        self.engine = None
        self.base = declarative_base()

    def initSession(self):
        global initialized
        if self._config.CONNECTION_MODE == ConnectionType.LOCAL_MEMORY:
            self.engine = create_engine("sqlite:///:memory:", echo = self._config.VERBOSE_OUTPUT)
        elif self._config.CONNECTION_MODE == ConnectionType.LOCAL_FILE:
            self.engine = create_engine(f"sqlite:///{self._config.LOCAL_FILENAME}", echo = self._config.VERBOSE_OUTPUT)
        elif self._config.CONNECTION_MODE == ConnectionType.REMOTE_SERVER:
            url_object = URL.create(
                "mysql+mysqldb",
                username = self._config.REMOTE_USERNAME,
                password = self._config.REMOTE_PASSWORD,
                host = self._config.REMOTE_HOST,
                database = self._config.SCHEMA,
            )
            # For "production", do not echo to output regardless if we have verbose mode on or not.
            self.engine = create_engine(url_object, echo = False)
        else:
            print("ERROR: Config value CONNECTION_MODE is not recognized. Check your config file!")
            sys.exit()

        self.session = sessionmaker(bind = self.engine)()

        if self._config.VERBOSE_OUTPUT:
            print(f"Connected via {self._config.CONNECTION_MODE}")

        initialized = True

    def generateEntry(self, dbEntry):
        # Creates the table if not done so already
        dbEntry.metadata.create_all(self.engine)
        self.session.add(dbEntry)
        self.session.commit()

    def getTableContents(self, dbEntry, tableEntries:list=None):
        if not dbEntry:
            return None
        if not tableEntries:
            tableEntries = self.session.query(dbEntry).all()
        elif not isinstance(tableEntries, list):
            tableEntries = [tableEntries]
        attributes = [attr for attr in dbEntry.__table__.columns.keys()]
        itemDict = dict()
        for item in tableEntries:
            itemEntry = {attr: getattr(item, attr) for attr in attributes if hasattr(item, attr)}
            # Hmm.. something is suspicious if our id key is missing.
            # For now we'll just back out of here; the user will be thrown an error about it.
            if not itemEntry.get('id'):
                return None
            itemId = itemEntry.pop('id')
            itemDict[itemId] = itemEntry

        print(f"id - {itemDict}")
        return itemDict


if __name__ == "__main__":
    from config.Config import Config

    testDB = DatabaseManager(Config)
    testDB.initSession()
