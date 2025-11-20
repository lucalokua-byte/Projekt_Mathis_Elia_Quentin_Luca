import os
import sys
import unittest

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from Db_maneger.Db_maneger import DBManager


class TestDbManager(unittest.TestCase):

    def setUp(self):

        #Setup a test database manager with a temporary file

        self.test_folder = "test_data"
        self.test_filename ="test_licence_plates.json"
        self.db = DBManager(self.test_folder, self.test_filename)

    def tearDown(self):

        #Clean up the test database file after tests

        test_file_path = os.path.join(self.test_folder,self.test_filename)
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if os.path.exists(self.test_folder):
            os.rmdir(self.test_folder)

    def test_add_license_plate(self):

        #Test adding a license plate

        result = self.db.add_license_plate("ABC123")
        self.assertTrue(result)
        self.assertIsNotNone(self.db.find("ABC123"))

    def test_add_existing_license_plate(self):

        #Test adding an existing license plate

        self.db.add_license_plate("ABC123")
        result = self.db.add_license_plate("ABC123")
        self.assertFalse(result)

    def test_remove_license_plate(self):

        #Test removing a license plate

        self.db.add_license_plate("XYZ789")
        result = self.db.remove_licence_plate("XYZ789")
        self.assertTrue(result)
        self.assertIsNone(self.db.find("XYZ789"))

    def test_remove_nonexistent_license_plate(self):

        #Test removing a non-existent license plate

        result = self.db.remove_license_plate("NONEXISTENT")
        self.assertFalse(result)
    
    def test_list_all(self):
        #Test listing all license plates

        self.db.add_license_plate("PLATE1")
        self.db.add_license_plate("PLATE2")
        all_plates = self.db.list_all()
        self.assertEqual(len(all_plates), 2)

    def test_find_license_plate(self):

        #Test finding a license plate

        self.db.add_license_plate("FINDME")
        record = self.db.find("FINDME")
        self.assertIsNotNone(record)
        self.assertEqual(record['license_plate'], "FINDME")

if __name__ == '__main__':
    unittest.main()
        