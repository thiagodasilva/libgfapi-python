# Copyright (c) 2012-2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import gluster
import os
import stat
import errno

from gluster import gfapi
from nose import SkipTest
from mock import Mock, patch
from contextlib import nested


def _mock_glfs_close(fd):
    return 0


def _mock_glfs_closedir(fd):
    return


def _mock_glfs_new(volid):
    return 2


def _mock_glfs_init(fs):
    return 0


def _mock_glfs_set_volfile_server(fs, proto, host, port):
    return


def _mock_glfs_fini(fs):
    return


class TestFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fd = gfapi.GlusterFile(2)

    @classmethod
    def tearDownClass(cls):
        cls.fd = None

    def setUp(self):
        self._saved_glfs_close = gluster.gfapi.api.glfs_close
        gluster.gfapi.api.glfs_close = _mock_glfs_close

    def tearDown(self):
        gluster.gfapi.api.glfs_close = self._saved_glfs_close

    def test_fchown_success(self):
        mock_glfs_fchown = Mock()
        mock_glfs_fchown.return_value = 0

        with patch("gluster.gfapi.api.glfs_fchown", mock_glfs_fchown):
            ret = self.fd.fchown(9, 11)
            self.assertEquals(ret, 0)

    def test_fchown_fail_exception(self):
        mock_glfs_fchown = Mock()
        mock_glfs_fchown.return_value = -1

        with patch("gluster.gfapi.api.glfs_fchown", mock_glfs_fchown):
            self.assertRaises(OSError, self.fd.fchown, 9, 11)

    def test_fdatasync_success(self):
        mock_glfs_fdatasync = Mock()
        mock_glfs_fdatasync.return_value = 4

        with patch("gluster.gfapi.api.glfs_fdatasync", mock_glfs_fdatasync):
            ret = self.fd.fdatasync()
            self.assertEquals(ret, 4)

    def test_fdatasync_fail_exception(self):
        mock_glfs_fdatasync = Mock()
        mock_glfs_fdatasync.return_value = -1

        with patch("gluster.gfapi.api.glfs_fdatasync", mock_glfs_fdatasync):
            self.assertRaises(OSError, self.fd.fdatasync)

    def test_fstat_success(self):
        mock_glfs_fstat = Mock()
        mock_glfs_fstat.return_value = 0

        with patch("gluster.gfapi.api.glfs_fstat", mock_glfs_fstat):
            s = self.fd.fstat()
            self.assertTrue(isinstance(s, gfapi.Stat))

    def test_fstat_fail_exception(self):
        mock_glfs_fstat = Mock()
        mock_glfs_fstat.return_value = -1

        with patch("gluster.gfapi.api.glfs_fstat", mock_glfs_fstat):
            self.assertRaises(OSError, self.fd.fstat)

    def test_fsync_success(self):
        mock_glfs_fsync = Mock()
        mock_glfs_fsync.return_value = 4

        with patch("gluster.gfapi.api.glfs_fsync", mock_glfs_fsync):
            ret = self.fd.fsync()
            self.assertEquals(ret, 4)

    def test_fsync_fail_exception(self):
        mock_glfs_fsync = Mock()
        mock_glfs_fsync.return_value = -1

        with patch("gluster.gfapi.api.glfs_fsync", mock_glfs_fsync):
            self.assertRaises(OSError, self.fd.fsync)

    def test_read_success(self):
        def _mock_glfs_read(fd, rbuf, buflen, flags):
            rbuf.value = "hello"
            return 5

        with patch("gluster.gfapi.api.glfs_read", _mock_glfs_read):
            b = self.fd.read(5)
            self.assertEqual(b.value, "hello")

    def test_read_fail_exception(self):
        mock_glfs_read = Mock()
        mock_glfs_read.return_value = -1

        with patch("gluster.gfapi.api.glfs_read", mock_glfs_read):
            self.assertRaises(OSError, self.fd.read, 5)

    def test_read_fail_empty_buffer(self):
        mock_glfs_read = Mock()
        mock_glfs_read.return_value = 0

        with patch("gluster.gfapi.api.glfs_read", mock_glfs_read):
            b = self.fd.read(5)
            self.assertEqual(b, 0)

    def test_write_success(self):
        mock_glfs_write = Mock()
        mock_glfs_write.return_value = 5

        with patch("gluster.gfapi.api.glfs_write", mock_glfs_write):
            ret = self.fd.write("hello")
            self.assertEqual(ret, 5)

    def test_write_binary_success(self):
        mock_glfs_write = Mock()
        mock_glfs_write.return_value = 3

        with patch("gluster.gfapi.api.glfs_write", mock_glfs_write):
            b = bytearray(3)
            ret = self.fd.write(b)
            self.assertEqual(ret, 3)

    def test_write_fail_exception(self):
        mock_glfs_write = Mock()
        mock_glfs_write.return_value = -1

        with patch("gluster.gfapi.api.glfs_write", mock_glfs_write):
            self.assertRaises(OSError, self.fd.write, "hello")

    def test_fallocate_success(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_fallocate = Mock()
        mock_glfs_fallocate.return_value = 0

        with patch("gluster.gfapi.api.glfs_fallocate", mock_glfs_fallocate):
            ret = self.fd.fallocate(0, 0, 1024)
            self.assertEqual(ret, 0)

    def test_fallocate_fail_exception(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_fallocate = Mock()
        mock_glfs_fallocate.return_value = -1

        with patch("gluster.gfapi.api.glfs_fallocate", mock_glfs_fallocate):
            self.assertRaises(OSError, self.fd.fallocate, 0, 0, 1024)

    def test_discard_success(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_discard = Mock()
        mock_glfs_discard.return_value = 0

        with patch("gluster.gfapi.api.glfs_discard", mock_glfs_discard):
            ret = self.fd.discard(1024, 1024)
            self.assertEqual(ret, 0)

    def test_discard_fail_exception(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_discard = Mock()
        mock_glfs_discard.return_value = -1

        with patch("gluster.gfapi.api.glfs_discard", mock_glfs_discard):
            self.assertRaises(OSError, self.fd.discard, 1024, 1024)


class TestDir(unittest.TestCase):

    def setUp(self):
        self._saved_glfs_closedir = gluster.gfapi.api.glfs_closedir
        gluster.gfapi.api.glfs_closedir = _mock_glfs_closedir

    def tearDown(self):
        gluster.gfapi.api.glfs_closedir = self._saved_glfs_closedir

    def test_next_success(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")

        def mock_glfs_readdir_r(fd, ent, cursor):
            cursor.contents = "bla"
            return 0

        with patch("gluster.gfapi.api.glfs_readdir_r", mock_glfs_readdir_r):
            fd = gfapi.GlusterDir(2)
            ent = fd.next()
            self.assertTrue(isinstance(ent, gfapi.Dirent))


class TestVolume(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._saved_glfs_new = gluster.gfapi.api.glfs_new
        gluster.gfapi.api.glfs_new = _mock_glfs_new

        cls._saved_glfs_set_volfile_server = \
            gluster.gfapi.api.glfs_set_volfile_server
        gluster.gfapi.api.glfs_set_volfile_server = \
            _mock_glfs_set_volfile_server

        cls._saved_glfs_init = gluster.gfapi.api.glfs_init
        gluster.gfapi.api.glfs_init = _mock_glfs_init

        cls._saved_glfs_fini = gluster.gfapi.api.glfs_fini
        gluster.gfapi.api.glfs_fini = _mock_glfs_fini

        cls._saved_glfs_close = gluster.gfapi.api.glfs_close
        gluster.gfapi.api.glfs_close = _mock_glfs_close

        cls._saved_glfs_closedir = gluster.gfapi.api.glfs_closedir
        gluster.gfapi.api.glfs_closedir = _mock_glfs_closedir
        cls.vol = gfapi.GlusterFilesystem("mockhost", "test")

    @classmethod
    def tearDownClass(cls):
        cls.vol = None
        gluster.gfapi.api.glfs_new = cls._saved_glfs_new
        gluster.gfapi.api.glfs_set_volfile_server = \
            cls._saved_glfs_set_volfile_server
        gluster.gfapi.api.glfs_fini = cls._saved_glfs_fini
        gluster.gfapi.api.glfs_close = cls._saved_glfs_close
        gluster.gfapi.api.glfs_closedir = cls._saved_glfs_closedir
        gluster.gfapi.api.glfs_init = cls._saved_glfs_init

    def test_chown_success(self):
        mock_glfs_chown = Mock()
        mock_glfs_chown.return_value = 0

        with patch("gluster.gfapi.api.glfs_chown", mock_glfs_chown):
            ret = self.vol.chown("file.txt", 9, 11)
            self.assertEquals(ret, 0)

    def test_chown_fail_exception(self):
        mock_glfs_chown = Mock()
        mock_glfs_chown.return_value = -1

        with patch("gluster.gfapi.api.glfs_chown", mock_glfs_chown):
            self.assertRaises(OSError, self.vol.chown, "file.txt", 9, 11)

    def test_creat_success(self):
        mock_glfs_creat = Mock()
        mock_glfs_creat.return_value = 2

        with patch("gluster.gfapi.api.glfs_creat", mock_glfs_creat):
            with self.vol.creat("file.txt", os.O_WRONLY, 0644) as fd:
                self.assertTrue(isinstance(fd, gfapi.GlusterFile))
                self.assertEqual(mock_glfs_creat.call_count, 1)
                mock_glfs_creat.assert_called_once_with(2,
                                                        "file.txt",
                                                        os.O_WRONLY, 0644)

    def test_creat_fail_exception(self):
        mock_glfs_creat = Mock()
        mock_glfs_creat.return_value = None

        def assert_creat():
            with self.vol.creat("file.txt", os.O_WRONLY, 0644) as fd:
                self.assertEqual(fd, None)

        with patch("gluster.gfapi.api.glfs_creat", mock_glfs_creat):
            self.assertRaises(OSError, assert_creat)

    def test_exists_true(self):
        mock_glfs_stat = Mock()
        mock_glfs_stat.return_value = 0

        with patch("gluster.gfapi.api.glfs_stat", mock_glfs_stat):
            ret = self.vol.exists("file.txt")
            self.assertTrue(ret)

    def test_not_exists_false(self):
        mock_glfs_stat = Mock()
        mock_glfs_stat.return_value = -1

        with patch("gluster.gfapi.api.glfs_stat", mock_glfs_stat):
            ret = self.vol.exists("file.txt")
            self.assertFalse(ret)

    def test_isdir_true(self):
        mock_glfs_stat = Mock()
        s = gfapi.Stat()
        s.st_mode = stat.S_IFDIR
        mock_glfs_stat.return_value = s

        with patch("gluster.gfapi.GlusterFilesystem.stat", mock_glfs_stat):
            ret = self.vol.isdir("dir")
            self.assertTrue(ret)

    def test_isdir_false(self):
        mock_glfs_stat = Mock()
        s = gfapi.Stat()
        s.st_mode = stat.S_IFREG
        mock_glfs_stat.return_value = s

        with patch("gluster.gfapi.GlusterFilesystem.stat", mock_glfs_stat):
            ret = self.vol.isdir("file")
            self.assertFalse(ret)

    def test_isdir_false_nodir(self):
        mock_glfs_stat = Mock()
        mock_glfs_stat.return_value = -1

        with patch("gluster.gfapi.api.glfs_stat", mock_glfs_stat):
            ret = self.vol.isdir("dirdoesnotexist")
            self.assertFalse(ret)

    def test_isfile_true(self):
        mock_glfs_stat = Mock()
        s = gfapi.Stat()
        s.st_mode = stat.S_IFREG
        mock_glfs_stat.return_value = s

        with patch("gluster.gfapi.GlusterFilesystem.stat", mock_glfs_stat):
            ret = self.vol.isfile("file")
            self.assertTrue(ret)

    def test_isfile_false(self):
        mock_glfs_stat = Mock()
        s = gfapi.Stat()
        s.st_mode = stat.S_IFDIR
        mock_glfs_stat.return_value = s

        with patch("gluster.gfapi.GlusterFilesystem.stat", mock_glfs_stat):
            ret = self.vol.isfile("dir")
            self.assertFalse(ret)

    def test_isfile_false_nofile(self):
        mock_glfs_stat = Mock()
        mock_glfs_stat.return_value = -1

        with patch("gluster.gfapi.api.glfs_stat", mock_glfs_stat):
            ret = self.vol.isfile("filedoesnotexist")
            self.assertFalse(ret)

    def test_islink_true(self):
        mock_glfs_lstat = Mock()
        s = gfapi.Stat()
        s.st_mode = stat.S_IFLNK
        mock_glfs_lstat.return_value = s

        with patch("gluster.gfapi.GlusterFilesystem.lstat", mock_glfs_lstat):
            ret = self.vol.islink("solnk")
            self.assertTrue(ret)

    def test_islink_false(self):
        mock_glfs_lstat = Mock()
        s = gfapi.Stat()
        s.st_mode = stat.S_IFREG
        mock_glfs_lstat.return_value = s

        with patch("gluster.gfapi.GlusterFilesystem.lstat", mock_glfs_lstat):
            ret = self.vol.islink("file")
            self.assertFalse(ret)

    def test_islink_false_nolink(self):
        mock_glfs_lstat = Mock()
        mock_glfs_lstat.return_value = -1

        with patch("gluster.gfapi.api.glfs_lstat", mock_glfs_lstat):
            ret = self.vol.islink("linkdoesnotexist")
            self.assertFalse(ret)

    def test_getxattr_success(self):
        def mock_glfs_getxattr(fs, path, key, buf, maxlen):
            buf.value = "fake_xattr"
            return 10

        with patch("gluster.gfapi.api.glfs_getxattr", mock_glfs_getxattr):
            buf = self.vol.getxattr("file.txt", "key1", 32)
            self.assertEquals("fake_xattr", buf)

    def test_getxattr_fail_exception(self):
        mock_glfs_getxattr = Mock()
        mock_glfs_getxattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_getxattr", mock_glfs_getxattr):
            self.assertRaises(IOError, self.vol.getxattr, "file.txt",
                              "key1", 32)

    def test_listdir_success(self):
        mock_glfs_opendir = Mock()
        mock_glfs_opendir.return_value = 2

        dirent1 = gfapi.Dirent()
        dirent1.d_name = "mockfile"
        dirent1.d_reclen = 8
        dirent2 = gfapi.Dirent()
        dirent2.d_name = "mockdir"
        dirent2.d_reclen = 7
        dirent3 = gfapi.Dirent()
        dirent3.d_name = "."
        dirent3.d_reclen = 1
        mock_Dir_next = Mock()
        mock_Dir_next.side_effect = [dirent1, dirent2, dirent3, None]

        with nested(patch("gluster.gfapi.api.glfs_opendir", mock_glfs_opendir),
                    patch("gluster.gfapi.GlusterDir.next", mock_Dir_next)):
            d = self.vol.listdir("testdir")
            self.assertEqual(len(d), 2)
            self.assertEqual(d[0], 'mockfile')

    def test_listdir_fail_exception(self):
        mock_glfs_opendir = Mock()
        mock_glfs_opendir.return_value = None

        with patch("gluster.gfapi.api.glfs_opendir", mock_glfs_opendir):
            self.assertRaises(OSError, self.vol.listdir, "test.txt")

    def test_listxattr_success(self):
        def mock_glfs_listxattr(fs, path, buf, buflen):
            buf.raw = "key1\0key2\0"
            return 10

        with patch("gluster.gfapi.api.glfs_listxattr", mock_glfs_listxattr):
            xattrs = self.vol.listxattr("file.txt")
            self.assertTrue("key1" in xattrs)
            self.assertTrue("key2" in xattrs)

    def test_listxattr_fail_exception(self):
        mock_glfs_listxattr = Mock()
        mock_glfs_listxattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_listxattr", mock_glfs_listxattr):
            self.assertRaises(IOError, self.vol.listxattr, "file.txt")

    def test_lstat_success(self):
        mock_glfs_lstat = Mock()
        mock_glfs_lstat.return_value = 0

        with patch("gluster.gfapi.api.glfs_lstat", mock_glfs_lstat):
            s = self.vol.lstat("file.txt")
            self.assertTrue(isinstance(s, gfapi.Stat))

    def test_lstat_fail_exception(self):
        mock_glfs_lstat = Mock()
        mock_glfs_lstat.return_value = -1

        with patch("gluster.gfapi.api.glfs_lstat", mock_glfs_lstat):
            self.assertRaises(OSError, self.vol.lstat, "file.txt")

    def test_stat_success(self):
        mock_glfs_stat = Mock()
        mock_glfs_stat.return_value = 0

        with patch("gluster.gfapi.api.glfs_stat", mock_glfs_stat):
            s = self.vol.stat("file.txt")
            self.assertTrue(isinstance(s, gfapi.Stat))

    def test_stat_fail_exception(self):
        mock_glfs_stat = Mock()
        mock_glfs_stat.return_value = -1

        with patch("gluster.gfapi.api.glfs_stat", mock_glfs_stat):
            self.assertRaises(OSError, self.vol.stat, "file.txt")

    def test_makedirs_success(self):
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.side_effect = [0, 0]

        mock_exists = Mock()
        mock_exists.side_effect = (False, True, False)

        with nested(patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir),
                    patch("gluster.gfapi.GlusterFilesystem.exists",
                          mock_exists)):
            self.vol.makedirs("dir1/", 0775)
            self.assertEqual(mock_glfs_mkdir.call_count, 1)
            mock_glfs_mkdir.assert_any_call(self.vol.fs, "dir1/", 0775)

    def test_makedirs_success_EEXIST(self):
        err = errno.EEXIST
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.side_effect = [OSError(err, os.strerror(err)), 0]

        mock_exists = Mock()
        mock_exists.side_effect = [False, True, False]

        with nested(patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir),
                    patch("gluster.gfapi.GlusterFilesystem.exists",
                          mock_exists)):
            self.vol.makedirs("./dir1/dir2", 0775)
            self.assertEqual(mock_glfs_mkdir.call_count, 2)
            mock_glfs_mkdir.assert_any_call(self.vol.fs, "./dir1", 0775)
            mock_glfs_mkdir.assert_called_with(self.vol.fs, "./dir1/dir2",
                                               0775)

    def test_makedirs_fail_exception(self):
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.return_value = -1

        mock_exists = Mock()
        mock_exists.return_value = False

        with nested(patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir),
                    patch("gluster.gfapi.GlusterFilesystem.exists",
                          mock_exists)):
            self.assertRaises(OSError, self.vol.makedirs, "dir1/dir2", 0775)

    def test_mkdir_success(self):
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.return_value = 0

        with patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir):
            ret = self.vol.mkdir("testdir", 0775)
            self.assertEquals(ret, 0)

    def test_mkdir_fail_exception(self):
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.return_value = -1

        with patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir):
            self.assertRaises(OSError, self.vol.mkdir, "testdir", 0775)

    def test_open_success(self):
        mock_glfs_open = Mock()
        mock_glfs_open.return_value = 2

        with patch("gluster.gfapi.api.glfs_open", mock_glfs_open):
            with self.vol.open("file.txt", os.O_WRONLY) as fd:
                self.assertTrue(isinstance(fd, gfapi.GlusterFile))
                self.assertEqual(mock_glfs_open.call_count, 1)
                mock_glfs_open.assert_called_once_with(2,
                                                       "file.txt",
                                                       os.O_WRONLY)

    def test_open_fail_exception(self):
        mock_glfs_open = Mock()
        mock_glfs_open.return_value = None

        def assert_open():
            with self.vol.open("file.txt", os.O_WRONLY) as fd:
                self.assertEqual(fd, None)

        with patch("gluster.gfapi.api.glfs_open", mock_glfs_open):
            self.assertRaises(OSError, assert_open)

    def test_opendir_success(self):
        mock_glfs_opendir = Mock()
        mock_glfs_opendir.return_value = 2

        with patch("gluster.gfapi.api.glfs_opendir", mock_glfs_opendir):
            d = self.vol.opendir("testdir")
            self.assertTrue(isinstance(d, gfapi.GlusterDir))

    def test_opendir_fail_exception(self):
        mock_glfs_opendir = Mock()
        mock_glfs_opendir.return_value = None

        with patch("gluster.gfapi.api.glfs_opendir", mock_glfs_opendir):
            self.assertRaises(OSError, self.vol.opendir, "testdir")

    def test_rename_success(self):
        mock_glfs_rename = Mock()
        mock_glfs_rename.return_value = 0

        with patch("gluster.gfapi.api.glfs_rename", mock_glfs_rename):
            ret = self.vol.rename("file.txt", "newfile.txt")
            self.assertEquals(ret, 0)

    def test_rename_fail_exception(self):
        mock_glfs_rename = Mock()
        mock_glfs_rename.return_value = -1

        with patch("gluster.gfapi.api.glfs_rename", mock_glfs_rename):
            self.assertRaises(OSError, self.vol.rename,
                              "file.txt", "newfile.txt")

    def test_rmdir_success(self):
        mock_glfs_rmdir = Mock()
        mock_glfs_rmdir.return_value = 0

        with patch("gluster.gfapi.api.glfs_rmdir", mock_glfs_rmdir):
            ret = self.vol.rmdir("testdir")
            self.assertEquals(ret, 0)

    def test_rmdir_fail_exception(self):
        mock_glfs_rmdir = Mock()
        mock_glfs_rmdir.return_value = -1

        with patch("gluster.gfapi.api.glfs_rmdir", mock_glfs_rmdir):
            self.assertRaises(OSError, self.vol.rmdir, "testdir")

    def test_unlink_success(self):
        mock_glfs_unlink = Mock()
        mock_glfs_unlink.return_value = 0

        with patch("gluster.gfapi.api.glfs_unlink", mock_glfs_unlink):
            ret = self.vol.unlink("file.txt")
            self.assertEquals(ret, 0)

    def test_unlink_fail_exception(self):
        mock_glfs_unlink = Mock()
        mock_glfs_unlink.return_value = -1

        with patch("gluster.gfapi.api.glfs_unlink", mock_glfs_unlink):
            self.assertRaises(OSError, self.vol.unlink, "file.txt")

    def test_removexattr_success(self):
        mock_glfs_removexattr = Mock()
        mock_glfs_removexattr.return_value = 0

        with patch("gluster.gfapi.api.glfs_removexattr",
                   mock_glfs_removexattr):
            ret = self.vol.removexattr("file.txt", "key1")
            self.assertEquals(ret, 0)

    def test_removexattr_fail_exception(self):
        mock_glfs_removexattr = Mock()
        mock_glfs_removexattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_removexattr",
                   mock_glfs_removexattr):
            self.assertRaises(IOError, self.vol.removexattr, "file.txt",
                              "key1")

    def test_rmtree_success(self):
        dir1_list = ["dir2", "file"]
        empty_list = []
        mock_listdir = Mock()
        mock_listdir.side_effect = [dir1_list, empty_list]

        mock_isdir = Mock()
        mock_isdir.side_effect = [True, False]

        mock_unlink = Mock()
        mock_unlink.return_value = 0

        mock_rmdir = Mock()
        mock_rmdir.return_value = 0

        mock_islink = Mock()
        mock_islink.return_value = False

        with nested(patch("gluster.gfapi.GlusterFilesystem.listdir",
                          mock_listdir),
                    patch("gluster.gfapi.GlusterFilesystem.isdir", mock_isdir),
                    patch("gluster.gfapi.GlusterFilesystem.islink",
                          mock_islink),
                    patch("gluster.gfapi.GlusterFilesystem.unlink",
                          mock_unlink),
                    patch("gluster.gfapi.GlusterFilesystem.rmdir",
                          mock_rmdir)):
            self.vol.rmtree("dir1")
            mock_rmdir.assert_any_call("dir1/dir2")
            mock_unlink.assert_called_once_with("dir1/file")
            mock_rmdir.assert_called_with("dir1")

    def test_rmtree_listdir_exception(self):
        mock_listdir = Mock()
        mock_listdir.side_effect = [OSError]

        mock_islink = Mock()
        mock_islink.return_value = False

        with nested(patch("gluster.gfapi.GlusterFilesystem.listdir",
                          mock_listdir),
                    patch("gluster.gfapi.GlusterFilesystem.islink",
                          mock_islink)):
            self.assertRaises(OSError, self.vol.rmtree, "dir1")

    def test_rmtree_islink_exception(self):
        mock_islink = Mock()
        mock_islink.return_value = True

        with patch("gluster.gfapi.GlusterFilesystem.islink", mock_islink):
            self.assertRaises(OSError, self.vol.rmtree, "dir1")

    def test_rmtree_ignore_unlink_rmdir_exception(self):
        dir1_list = ["dir2", "file"]
        empty_list = []
        mock_listdir = Mock()
        mock_listdir.side_effect = [dir1_list, empty_list]

        mock_isdir = Mock()
        mock_isdir.side_effect = [True, False]

        mock_unlink = Mock()
        mock_unlink.side_effect = [OSError]

        mock_rmdir = Mock()
        mock_rmdir.side_effect = [0, OSError]

        mock_islink = Mock()
        mock_islink.return_value = False

        with nested(patch("gluster.gfapi.GlusterFilesystem.listdir",
                          mock_listdir),
                    patch("gluster.gfapi.GlusterFilesystem.isdir", mock_isdir),
                    patch("gluster.gfapi.GlusterFilesystem.islink",
                          mock_islink),
                    patch("gluster.gfapi.GlusterFilesystem.unlink",
                          mock_unlink),
                    patch("gluster.gfapi.GlusterFilesystem.rmdir",
                          mock_rmdir)):
            self.vol.rmtree("dir1", True)
            mock_rmdir.assert_any_call("dir1/dir2")
            mock_unlink.assert_called_once_with("dir1/file")
            mock_rmdir.assert_called_with("dir1")

    def test_setxattr_success(self):
        mock_glfs_setxattr = Mock()
        mock_glfs_setxattr.return_value = 0

        with patch("gluster.gfapi.api.glfs_setxattr", mock_glfs_setxattr):
            ret = self.vol.setxattr("file.txt", "key1", "hello", 5)
            self.assertEquals(ret, 0)

    def test_setxattr_fail_exception(self):
        mock_glfs_setxattr = Mock()
        mock_glfs_setxattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_setxattr", mock_glfs_setxattr):
            self.assertRaises(IOError, self.vol.setxattr, "file.txt",
                              "key1", "hello", 5)

    def test_symlink_success(self):
        mock_glfs_symlink = Mock()
        mock_glfs_symlink.return_value = 0

        with patch("gluster.gfapi.api.glfs_symlink", mock_glfs_symlink):
            ret = self.vol.symlink("file.txt", "filelink")
            self.assertEquals(ret, 0)

    def test_symlink_fail_exception(self):
        mock_glfs_symlink = Mock()
        mock_glfs_symlink.return_value = -1

        with patch("gluster.gfapi.api.glfs_symlink", mock_glfs_symlink):
            self.assertRaises(OSError, self.vol.symlink, "file.txt",
                              "filelink")

    def test_walk_success(self):
        dir1_list = ["dir2", "file"]
        empty_list = []
        mock_listdir = Mock()
        mock_listdir.side_effect = [dir1_list, empty_list]

        mock_isdir = Mock()
        mock_isdir.side_effect = [True, False]

        with nested(patch("gluster.gfapi.GlusterFilesystem.listdir",
                          mock_listdir),
                    patch("gluster.gfapi.GlusterFilesystem.isdir",
                          mock_isdir)):
            for (path, dirs, files) in self.vol.walk("dir1"):
                self.assertEqual(dirs, ['dir2'])
                self.assertEqual(files, ['file'])
                break

    def test_walk_listdir_exception(self):
        mock_listdir = Mock()
        mock_listdir.side_effect = [OSError]

        def mock_onerror(err):
            self.assertTrue(isinstance(err, OSError))

        with patch("gluster.gfapi.GlusterFilesystem.listdir", mock_listdir):
            for (path, dirs, files) in self.vol.walk("dir1",
                                                     onerror=mock_onerror):
                pass
