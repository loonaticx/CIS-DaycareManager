# DO NOT REMOVE THESE IMPORTS
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from uuid import uuid4
import secrets

from base.DatabaseManager import *
from config.Config import Config

Database = DatabaseManager(Config)
Database.initSession()

Base = Database.base
