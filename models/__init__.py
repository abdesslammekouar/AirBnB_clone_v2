#!/usr/bin/python3
"""This module instantiates an instance of the Storage will be used"""
from models.engine.file_storage import FileStorage
from os import getenv

storage_type = getenv('HBNB_TYPE_STORAGE')

if storage_type == 'db':
    from models.engine.db_storage import DBStorage
    storage = DBStorage()
else:
    storage = FileStorage()

storage.reload()
