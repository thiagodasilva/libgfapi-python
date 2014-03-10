import ctypes
import os
import basefilesystem as fs

from ctypes.util import find_library
from contextlib import contextmanager

# Looks like ctypes is having trouble with dependencies, so just force them to
# load with RTLD_GLOBAL until I figure that out.
api = ctypes.CDLL(find_library("gfapi"), ctypes.RTLD_GLOBAL, use_errno=True)

# Wow, the Linux kernel folks really play nasty games with this structure.  If
# you look at the man page for stat(2) and then at this definition you'll note
# two discrepancies.  First, we seem to have st_nlink and st_mode reversed.  In
# fact that's exactly how they're defined *for 64-bit systems*; for 32-bit
# they're in the man-page order.  Even uglier, the man page makes no mention of
# the *nsec fields, but they are very much present and if they're not included
# then we get memory corruption because libgfapi has a structure definition
# that's longer than ours and they overwrite some random bit of memory after
# the space we allocated.  Yes, that's all very disgusting, and I'm still not
# sure this will really work on 32-bit because all of the field types are so
# obfuscated behind macros and feature checks.


class Stat (ctypes.Structure):
    _fields_ = [
        ("st_dev", ctypes.c_ulong),
        ("st_ino", ctypes.c_ulong),
        ("st_nlink", ctypes.c_ulong),
        ("st_mode", ctypes.c_uint),
        ("st_uid", ctypes.c_uint),
        ("st_gid", ctypes.c_uint),
        ("st_rdev", ctypes.c_ulong),
        ("st_size", ctypes.c_ulong),
        ("st_blksize", ctypes.c_ulong),
        ("st_blocks", ctypes.c_ulong),
        ("st_atime", ctypes.c_ulong),
        ("st_atimensec", ctypes.c_ulong),
        ("st_mtime", ctypes.c_ulong),
        ("st_mtimensec", ctypes.c_ulong),
        ("st_ctime", ctypes.c_ulong),
        ("st_ctimensec", ctypes.c_ulong),
    ]


class Dirent (ctypes.Structure):
    _fields_ = [
        ("d_ino", ctypes.c_ulong),
        ("d_off", ctypes.c_ulong),
        ("d_reclen", ctypes.c_ushort),
        ("d_type", ctypes.c_char),
        ("d_name", ctypes.c_char * 256),
    ]

api.glfs_creat.restype = ctypes.c_void_p
api.glfs_open.restype = ctypes.c_void_p
api.glfs_lstat.restype = ctypes.c_int
api.glfs_lstat.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
                           ctypes.POINTER(Stat)]
api.glfs_opendir.restype = ctypes.c_void_p
api.glfs_readdir_r.restype = ctypes.c_int
api.glfs_readdir_r.argtypes = [ctypes.c_void_p, ctypes.POINTER(Dirent),
                               ctypes.POINTER(ctypes.POINTER(Dirent))]


class GlusterFile(fs.BaseFile):

    def __init__(self, fd):
        self.fd = fd

    # File operations, in alphabetical order.

    def close(self):
        ret = api.glfs_close(self.fd)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def discard(self, offset, len):
        ret = api.glfs_discard(self.fd, offset, len)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def fallocate(self, mode, offset, len):
        ret = api.glfs_fallocate(self.fd, mode, offset, len)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def fsync(self):
        ret = api.glfs_fsync(self.fd)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def read(self, buflen, flags=0):
        rbuf = ctypes.create_string_buffer(buflen)
        ret = api.glfs_read(self.fd, rbuf, buflen, flags)
        if ret > 0:
            return rbuf
        elif ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        else:
            return ret

    def write(self, data):
        # creating a ctypes.c_ubyte buffer to handle converting bytearray
        # to the required C data type
        if type(data) is bytearray:
            buf = (ctypes.c_ubyte * len(data)).from_buffer(data)
        else:
            buf = data
        ret = api.glfs_write(self.fd, buf, len(buf))
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret


class GlusterDir(fs.BaseDir):

    def __init__(self, fd):
        # Add a reference so the module-level variable "api" doesn't
        # get yanked out from under us (see comment above File def'n).
        self._api = api
        self.fd = fd
        self.cursor = ctypes.POINTER(Dirent)()

    def __del__(self):
        self._api.glfs_closedir(self.fd)
        self._api = None

    def next(self):
        entry = Dirent()
        entry.d_reclen = 256
        rc = api.glfs_readdir_r(self.fd, ctypes.byref(entry),
                                ctypes.byref(self.cursor))

        if (rc < 0) or (not self.cursor) or (not self.cursor.contents):
            return rc

        return entry


class GlusterFilesystem(fs.BaseFilesystem):

    def __init__(self, host, volid, proto="tcp", port=24007):
        # Add a reference so the module-level variable "api" doesn't
        # get yanked out from under us.
        self._api = api
        self.xattr_default_size = 256
        self.fs = api.glfs_new(volid)
        api.glfs_set_volfile_server(self.fs, proto, host, port)
        api.glfs_init(self.fs)

    def __del__(self):
        self._api.glfs_fini(self.fs)
        self._api = None

    def set_logging(self, path, level):
        api.glfs_set_logging(self.fs, path, level)

    # File operations, in alphabetical order.

    @contextmanager
    def creat(self, path, flags, mode):
        fd = api.glfs_creat(self.fs, path, flags, mode)
        if not fd:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))

        fileobj = None
        try:
            fileobj = GlusterFile(fd)
            yield fileobj
        finally:
            fileobj.close()

    #def getxattr(self, path, key, maxlen):
    def getxattr(self, path, key, nofollow=False):
        buf = ctypes.create_string_buffer(self.xattr_default_size)
        rc = api.glfs_getxattr(self.fs, path, key, buf,
                               self.xattr_default_size)
        if rc < 0:
            err = ctypes.get_errno()
            raise IOError(err, os.strerror(err))
        return buf.value[:rc]

    def listxattr(self, path, nofollow=False):
        buf = ctypes.create_string_buffer(512)
        rc = api.glfs_listxattr(self.fs, path, buf, 512)
        if rc < 0:
            err = ctypes.get_errno()
            raise IOError(err, os.strerror(err))
        xattrs = []
        # Parsing character by character is ugly, but it seems like the
        # easiest way to deal with the "strings separated by NUL in one
        # buffer" format.
        i = 0
        while i < rc:
            new_xa = buf.raw[i]
            i += 1
            while i < rc:
                next_char = buf.raw[i]
                i += 1
                if next_char == '\0':
                    xattrs.append(new_xa)
                    break
                new_xa += next_char
        xattrs.sort()
        return xattrs

    def lstat(self, path):
        x = Stat()
        rc = api.glfs_lstat(self.fs, path, ctypes.byref(x))
        if rc < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return x

    def mkdir(self, path, mode):
        ret = api.glfs_mkdir(self.fs, path, mode)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    @contextmanager
    def open(self, path, flags):
        fd = api.glfs_open(self.fs, path, flags)
        if not fd:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))

        fileobj = None
        try:
            fileobj = GlusterFile(fd)
            yield fileobj
        finally:
            fileobj.close()

    def opendir(self, path):
        fd = api.glfs_opendir(self.fs, path)
        if not fd:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return GlusterDir(fd)

    def rename(self, src, dst):
        ret = api.glfs_rename(self.fs, src, dst)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def rmdir(self, path):
        ret = api.glfs_rmdir(self.fs, path)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def setxattr(self, path, key, value, flags=0):
        ret = api.glfs_setxattr(self.fs, path, key, value, len(value), flags)
        if ret < 0:
            err = ctypes.get_errno()
            raise IOError(err, os.strerror(err))
        return ret

    def unlink(self, path):
        ret = api.glfs_unlink(self.fs, path)
        if ret < 0:
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err))
        return ret

    def _mode2flags(self, mode):
        flags = os.O_RDONLY
        if (mode in ['r', 'rb', 'rt']):
            flags = os.O_RDONLY
        elif (mode in ['w', 'wb', 'wt']):
            flags = os.O_WRONLY
        elif (mode in ['rw']):
            flags = os.O_RDWR

        return flags
