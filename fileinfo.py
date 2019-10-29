import os

class File:
    def __init__(self, filename=None):
        self.__fn = None
        self.__ext = None
        self.__name = None
        self.__dir = None
        self.set_filename(filename)
        self.filename = property(fget=self.get_filename, fset=self.set_filename)
        self.name = property(fget=self.get_name)
        self.dir = property(fget=self.get_dir)
        self.ext = property(fget=self.get_ext)
        
    def __str__(self):
        return str(self.__fn)

    def get_filename(self):
        return self.__fn

    def set_filename(self, value):

        def __g_ext():
            acc = ""
            count = len(value)
            i = count
            for i in range(count-1,-1,-1):
                if value[i] == ".": break
            if i == 0 : return None
            for j in range(i+1,count):
                acc += value[j]
            return acc.lower()

        self.__fn = value
        if value is None:
            self.__ext = None
            self.__name = None
            self.__dir = None
        else:
            self.__dir = os.path.dirname(self.__fn)
            self.__ext = __g_ext()
            self.__name = os.path.basename(self.__fn)

    def get_ext(self):
        return self.__ext

    def get_name(self):
        return self.__name

    def get_dir(self):
        return self.__dir



