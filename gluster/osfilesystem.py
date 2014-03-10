import basefilesystem as fs
import xattr
import os

from contextlib import contextmanager


class OSFilesytem(fs.BaseFilesystem):

    def getxattr(self, path, key, nofollow=False):
        return xattr.get(path, key, nofollow)

    def listxattr(self, path, nofollow=False):
        return xattr.list(path, nofollow)

    def lstat(self, path):
        return os.lstat(path)

    def mkdir(self, path, mode=0777):
        return os.mkdir(path, mode)

    @contextmanager
    def open(self, path, mode='r'):
        f = open(path, mode)
        try:
            fileobj = OSFile(f)
            yield fileobj
        finally:
            fileobj.close()

    def opendir(self, path):
        raise IOError

    def rename(self, src, dst):
        return os.rename(src, dst)

    def rmdir(self, path):
        return os.rmdir(path)

    def setxattr(self, path, key, value, flags=0):
        xattr.set(path, key, value, flags)

    def unlink(self, path):
        return os.unlink(path)


class OSFile(fs.BaseFile):

    def __init__(self, f):
        self._file = f

    def close(self):
        return self._file.close()

    def fsync(self):
        self._file.flush()
        os.fsync(self._file.fileno())

    def read(self, size):
        self._file.read(size)

    def write(self, data):
        self._file.write(data)
