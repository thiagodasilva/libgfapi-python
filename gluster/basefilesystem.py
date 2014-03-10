from abc import ABCMeta, abstractmethod


class BaseFilesystem(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getxattr(self, path, key, nofollow=False):
        pass

    @abstractmethod
    def listxattr(self, path, nofollow=False):
        pass

    @abstractmethod
    def lstat(self, path):
        pass

    @abstractmethod
    def mkdir(self, path, mode):
        pass

    @abstractmethod
    def open(self, path, mode):
        pass

    @abstractmethod
    def opendir(self, path):
        pass

    @abstractmethod
    def rename(self, src, dst):
        pass

    @abstractmethod
    def rmdir(self, path):
        pass

    @abstractmethod
    def setxattr(self, path, key, value, flags):
        pass

    @abstractmethod
    def unlink(self, path):
        pass


class BaseDir(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def next(self):
        pass


class BaseFile(object):
    __metaclass__ = ABCMeta

    def __init__(self, f):
        self._file = f

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def fsync(self):
        pass

    @abstractmethod
    def read(self, size):
        pass

    @abstractmethod
    def write(self, data):
        pass
