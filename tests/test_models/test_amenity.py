#!/usr/bin/python3
""" """
from tests.test_models.test_base_model import test_basemodel
from models.amenity import Amenity
import os


class test_Amenity(test_basemodel):
    """ amenity test class"""

    def __init__(self, *args, **kwargs):
        """ Initialize the test class """
        super().__init__(*args, **kwargs)
        self.name = "Amenity"
        self.value = Amenity

    def test_name2(self):
        """ Testing name type """
        new = self.value()
        expected_type = str if os.getenv('HBNB_TYPE_STORAGE') != 'db' else type(None)
        self.assertEqual(type(new.name), expected_type)

