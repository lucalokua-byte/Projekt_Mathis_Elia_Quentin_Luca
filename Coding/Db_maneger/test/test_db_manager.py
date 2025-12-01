import os
import sys
import unittest

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import Db_maneger as DBManager


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
        result = self.db.remove_license_plate("XYZ789")
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

    def test_blacklist_plate(self):
        self.db.blacklist_plate("BLACK123")
        self.assertIn("BLACK123", self.db.blacklisted_plates)

    def test_whitelist_plate(self):
        self.db.whitelist_plate("WHITE123")
        self.assertIn("WHITE123", self.db.whitelisted_plates)

    def test_blacklist_to_whitelist_transition(self):
        self.db.blacklist_plate("SWITCH123")
        self.db.whitelist_plate("SWITCH123")
        self.assertNotIn("SWITCH123", self.db.blacklisted_plates)
        self.assertIn("SWITCH123", self.db.whitelisted_plates)
        
    def test_add_plate_whitelist_enforced_reject(self):
        self.db.enforce_Whielist = True
        self.db.whitelist_plate("ALLOWED123")
        result = self.db.add_license_plate("BLOCKED456")
        self.assertFalse(result)  # BLOCKED456 not whitelisted

    def test_add_blacklisted_plate_should_fail(self):
        self.db.blacklist_plate("BAD123")
        result = self.db.add_license_plate("BAD123")
        self.assertFalse(result)

    def test_clear_database(self):
        self.db.add_license_plate("TO_CLEAR")
        self.db.clear_database()
        self.assertEqual(len(self.db.list_all()), 0)



if __name__ == '__main__':
    unittest.main()
        