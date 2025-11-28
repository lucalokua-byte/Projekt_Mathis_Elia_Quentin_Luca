from abc import ABC, abstractmethod

class AbstractDBManager(ABC):

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

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

    

