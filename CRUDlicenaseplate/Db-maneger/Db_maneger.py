import json
import os 

class DBManger:

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
