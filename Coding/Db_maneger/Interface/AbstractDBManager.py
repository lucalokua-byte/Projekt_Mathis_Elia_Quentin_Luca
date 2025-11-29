from abc import ABC, abstractmethod

class AbstractDBManager(ABC):

    @abstractmethod
    def add_license_plate(self, license_plate):
        pass        

    @abstractmethod
    def remove_license_plate(self, license_plate):
        pass

    @abstractmethod
    def find(self, license_plate, verbose=True):
        pass

    @abstractmethod
    def list_all(self):
        pass    

    @abstractmethod
    def clear_database(self):
        pass

    @abstractmethod
    def blacklist_plate(self, license_plate):
        pass    
    
    @abstractmethod
    def whitelist_plate(self, license_plate):
        pass    

    




    

