import json
import os
import time 

from Db_maneger.AbstractDBManager import AbstractDBManager
class DBManager(AbstractDBManager):#Dbmanager_Json

    def __init__(self,folder,filename):

        #Ensure the folder exists if not its create one
        os.makedirs(folder, exist_ok=True)

        #Full path to the database JSON file 
        self.filename = os.path.join(folder,filename)

        #Initernal list to store the Blacklisted license plates
        self.blacklisted_plates = set()

        #Initernal list to store the Whitelisted license plates
        self.whitelisted_plates = set()

        # Whitelist is optional by defult (soft Rule)
        self.enforce_Whielist = False 

        # Vistor log
        self.visitor_log = set()

        # whitelist log
        self.whitelist_log = set()
        # Blacklist log
        self.blacklist_log = set()



        #Load existing data from the JSON file if it exists
        self.load_data()
        
    def load_data(self):
        #Load data from the JSON file if it exists
        if os.path.exists(self.filename):
            with open(self.filename,'r', encoding='utf-8') as file: # 'r' mode for reading
                try:
                    # Try to load data as a dictionary with specific keys
                    data=json.load(file)
                    # Case1:New Format (dictionary with keys)
                    if isinstance(data, dict):
                        # Load visitor, whitelist and blacklist logs
                        self.visitor_log = data.get('visitors', []) 
                        self.whitelist_log = data.get('whitelist_log', [])
                        self.blacklist_log = data.get('blacklist_log', [])
                        # Load license plates, whitelisted and blacklisted plates from the dictionary
                        self.whitelisted_plates = set(data.get('Whitelisted_plates', []))
                        self.blacklisted_plates = set(data.get('Blacklisted_plates', []))
                    # Case2:Old Format (list of license plates)
                    elif isinstance(data, list):
                        # Just assign to licenese_plates; no list exists yet
                        self.visitor_log = data
                        self.whitelisted_plates = set()
                        self.blacklisted_plates = set()
                    # Case3: Invalid Format
                    else:
                        raise ValueError("Invalid data format in JSON file.")
                except json.JSONDecodeError:
                    # json file exists but is empty or corrupted
                    print("Error decoding JSON file. Starting with an empty database.")
                    self.visitor_log = []
                    self.whitelist_log = []
                    self.blacklist_log = []
                    self.whitelisted_plates = set()
                    self.blacklisted_plates = set()
        else:
            # File does not exist; start with empty database
            self.visitor_log = []
            self.whitelist_log = []
            self.blacklist_log = []
            self.whitelisted_plates = set()
            self.blacklisted_plates = set()

    def save_data(self):
        # Preare the data to be saved in the new format
        data={
            'visitors': self.visitor_log,
            'whitelist_log': self.whitelist_log,
            'blacklist_log': self.blacklist_log,

            'Whitelisted_plates': list(self.whitelisted_plates),
            'Blacklisted_plates': list(self.blacklisted_plates)
        }
        # Save it to the file in pretty JSON format
        with open(self.filename, 'w', encoding='utf-8') as file: # 'w' mode for writing
            json.dump(data, file, indent=4) # indent=4 for pretty printing

    def add_license_plate(self, license_plate, confidence= None):
      
        # Record entry with timestamp
        entry = {
                    'license_plate': license_plate,
                    'date_added':time.strftime('%Y-%m-%d %H:%M:%S'),
                    'confidence': confidence
                    }
         #confidence lvl is optional parameter
        if confidence is not None:
         entry['confidence'] = confidence
        
        # Check blacklist and whitelist before adding
        if license_plate in self.blacklisted_plates:
            # log the attempt to add a blacklisted plate
            self.blacklist_log.append(entry)
            print(f"[BLACKLISTED]License plate '{license_plate}': is blacklisted and cannot be added.")
            self.save_data()
            return False
        # Optional Whitelist enforcement
        if self.enforce_Whielist and self.whitelisted_plates and license_plate not in self.whitelisted_plates:
            # log the attempt to add a non-whitelisted plate
            self.visitor_log.append(entry)
            print(f"[NOT WHITELISTED]License plate '{license_plate}': is not whitelisted")
            return False

        
        # Check if the license plate already exists
        if  self.find(license_plate, verbose=False):
            print(f"[EXISTS]License plate '{license_plate}' already exists in database.")
            return False
        # Log in the appropriate log
        if license_plate in self.whitelisted_plates:
         self.whitelist_log.append(entry)
         print(f"[WHITELISTED]License plate '{license_plate}' added successfully.")
        else:
            self.visitor_log.append(entry)
            print(f"[UNLISTED]License plate '{license_plate}' added successfully.")
            self.save_data()
        return True
    
    def remove_license_plate(self, license_plate):

        #Remove a license plate from the database if it exists.
        #Returns True if removed, False if not found.

        for record in self.visitor_log:
            if record['license_plate'] == license_plate:
                self.visitor_log.remove(record)
                self.save_data()
                return True
        return False
    
   
    def find(self, license_plate, verbose=True):
     for record in self.visitor_log:
        if record['license_plate'] == license_plate:
            if verbose: # added parameter to control verbosity(verbosity is added)
             print(f"License plate '{license_plate}' found in database.")
            return record
     if verbose:   
      print(f"License plate '{license_plate}' NOT found in database.")
     return None
    
    
    def list_all(self):
        #Return a list of all license plates in the database.
        return self.visitor_log
    
    def clear_database(self):
        #Clear all license plates from the database.
        self.visitor_log = []
        self.save_data()

    def blacklist_plate(self, license_plate):
        #Add a license plate to the blacklist.
        if license_plate not in self.blacklisted_plates:
            self.blacklisted_plates.add(license_plate)
            return True
        return False
    
    def whitelist_plate(self, license_plate):
        #Add a license plate to the whitelist.
        if license_plate not in self.whitelisted_plates:
            self.whitelisted_plates.add(license_plate)
            return True
        return False
    
    


 
 
 
if __name__ == "__main__":
    db_manager = DBManager("data", "licence_plates.json")

    db_manager.enforce_Whielist = False  # Desable whitelist enforcement
# clear existing data for demonstration purposes
    db_manager.clear_database()
    # Add plates to whitelist and blacklist using the methods
    db_manager.whitelist_plate("ABC123")
    db_manager.whitelist_plate("XYZ789")
    db_manager.blacklist_plate("DEF456")
    db_manager.blacklist_plate("GHI789")

    # Try adding different plates
    db_manager.add_license_plate("ABC123",confidence=90.2)  # Whitelisted – should succeed
    db_manager.add_license_plate("DEF456")  # Blacklisted – should fail
    db_manager.add_license_plate("LMN456")  # Not whitelisted – should fail if is whitelist enforced-> True
 
 
