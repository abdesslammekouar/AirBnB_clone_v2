#!/usr/bin/python3
"""This module defines a base class for all models in our hbnb clone"""
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from models import storage  # Assuming storage is properly imported

Base = declarative_base()


class BaseModel(Base):
    """A base class for all hbnb models"""
    __tablename__ = 'base_model'  # Define your table name

    id = Column(String(60), nullable=False, primary_key=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        """Instantiates a new model"""
        if not kwargs:
            self.id = str(uuid.uuid4())
            self.created_at = self.updated_at = datetime.utcnow()
        else:
            for k, v in kwargs.items():
                if k in ['created_at', 'updated_at']:
                    try:
                        setattr(self, k, datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f"))
                    except ValueError:
                        pass  # Handle datetime parsing errors gracefully
                elif k != '__class__':
                    setattr(self, k, v)

    def __str__(self):
        """Returns a string representation of the instance"""
        return '[{}] ({}) {}'.format(type(self).__name__, self.id, self.__dict__)

    def save(self):
        """Updates updated_at with the current time when the instance is changed"""
        self.updated_at = datetime.utcnow()
        storage.new(self)
        storage.save()

    def to_dict(self):
        """Converts the instance into a dict format"""
        dct = self.__dict__.copy()
        dct['__class__'] = type(self).__name__
        for k, v in dct.items():
            if isinstance(v, datetime):
                dct[k] = v.isoformat()
        return dct

    def delete(self):
        """Deletes the current instance from storage"""
        storage.delete(self)

