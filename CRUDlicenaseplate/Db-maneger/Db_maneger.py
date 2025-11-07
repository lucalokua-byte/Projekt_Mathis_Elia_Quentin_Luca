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
            with open(self.filename,'r', encoding='utf-8') as file:
                self.license_plates = json.load(file)
        else:
            self.license_plates = []
            
