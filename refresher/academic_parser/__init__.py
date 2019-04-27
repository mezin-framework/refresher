from abc import ABCMeta, abstractmethod

class AcademicApi(object):
    ''' Abstract class for AcademicApis '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_marks(self):
        pass

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def get_user_info(self):
        pass
