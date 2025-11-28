import json
import os
import sys

from Db_maneger.Interface.AbstractDBManager import AbstractDBManager
class DBManager(AbstractDBManager):

    def __init__(self,folder,filename):

        #Ensure the folder exists if not its create one
        os.makedirs(folder, exist_ok=True)

        #Full path to the database JSON file 
        self.filename = os.path.join(folder,filename)

        #Initernal list to store the license plates
        self.license_plates = []

        #Load existing data from the JSON file if it exists
        self.load_data()
        
    def load_data(self):
        #Load data from the JSON file if it exists
        if os.path.exists(self.filename):
            with open(self.filename,'r', encoding='utf-8') as file: # 'r' mode for reading
                self.license_plates = json.load(file)
        else:
            self.license_plates = []

    def save_data(self):
        #Save the current license plates to the JSON file
        with open(self.filename, 'w', encoding='utf-8') as file: # 'w' mode for writing
            json.dump(self.license_plates, file, indent=4) # indent=4 for pretty printing

    def add_license_plate(self, license_plate, confidence=None, timestamp=None, metadata=None):
        """
        Add a license plate to the database with additional information.
        Returns True if added, False if already exists.
        """
        if not self.find(license_plate, verbose=False):
            plate_data = {
                'license_plate': license_plate,
                'timestamp': timestamp or time.time(),
                'date_added': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add optional fields if provided
            if confidence is not None:
                plate_data['confidence'] = confidence
            if metadata:
                plate_data.update(metadata)
                
            self.license_plates.append(plate_data)
            self.save_data()
            print(f"✅ License plate '{license_plate}' added to database.")
            return True
        else:
            print(f"⚠️ License plate '{license_plate}' already exists in database.")
            return False
    
    def remove_license_plate(self, license_plate):

        #Remove a license plate from the database if it exists.
        #Returns True if removed, False if not found.

        for record in self.license_plates:
            if record['license_plate'] == license_plate:
                self.license_plates.remove(record)
                self.save_data()
                return True
        return False
    
   
    def find(self, license_plate, verbose=True):
     for record in self.license_plates:
        if record['license_plate'] == license_plate:
            if verbose: # added parameter to control verbosity(verbosity is added)
             print(f"License plate '{license_plate}' found in database.")
            return record
     if verbose:   
      print(f"License plate '{license_plate}' NOT found in database.")
     return None
    
    
    def list_all(self):
        #Return a list of all license plates in the database.
        return self.license_plates
    
    def clear_database(self):
        #Clear all license plates from the database.
        self.license_plates = []
        self.save_data()
    
    

# Example usage:
if __name__ == "__main__":
    db_manager = DBManager("data", "license_plates.json")
    db_manager.add_license_plate("ABC123")
    db_manager.add_license_plate("XYZ789")
    db_manager.add_license_plate("LMN456")
    db_manager.remove_license_plate("LMN456")
    db_manager.find("LMN456")
    db_manager.add_license_plate("ABC123")  # Attempt to add duplicate
    db_manager.add_license_plate("DEF321")
    print(db_manager.list_all())
    
 
