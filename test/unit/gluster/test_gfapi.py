import unittest
import gluster
import os

from gluster import gfapi
from nose import SkipTest
from mock import Mock, patch


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

    def setUp(self):
        self._saved_glfs_close = gluster.gfapi.api.glfs_close
        gluster.gfapi.api.glfs_close = _mock_glfs_close

    def tearDown(self):
        gluster.gfapi.api.glfs_close = self._saved_glfs_close

    def test_fsync_sucess(self):
        mock_glfs_fsync = Mock()
        mock_glfs_fsync.return_value = 4

        with patch("gluster.gfapi.api.glfs_fsync", mock_glfs_fsync):
            fd = gfapi.GlusterFile(2)
            ret = fd.fsync()
            self.assertEquals(ret, 4)

    def test_fsync_fail_exception(self):
        mock_glfs_fsync = Mock()
        mock_glfs_fsync.return_value = -1

        with patch("gluster.gfapi.api.glfs_fsync", mock_glfs_fsync):
            fd = gfapi.GlusterFile(2)
            self.assertRaises(OSError, fd.fsync)

    def test_read_success(self):
        def _mock_glfs_read(fd, rbuf, buflen, flags):
            rbuf.value = "hello"
            return 5

        with patch("gluster.gfapi.api.glfs_read", _mock_glfs_read):
            fd = gfapi.GlusterFile(2)
            b = fd.read(5)
            self.assertEqual(b.value, "hello")

    def test_read_fail_exception(self):
        mock_glfs_read = Mock()
        mock_glfs_read.return_value = -1

        with patch("gluster.gfapi.api.glfs_read", mock_glfs_read):
            fd = gfapi.GlusterFile(2)
            self.assertRaises(OSError, fd.read, 5)

    def test_read_fail_empty_buffer(self):
        mock_glfs_read = Mock()
        mock_glfs_read.return_value = 0

        with patch("gluster.gfapi.api.glfs_read", mock_glfs_read):
            fd = gfapi.GlusterFile(2)
            b = fd.read(5)
            self.assertEqual(b, 0)

    def test_write_success(self):
        mock_glfs_write = Mock()
        mock_glfs_write.return_value = 5

        with patch("gluster.gfapi.api.glfs_write", mock_glfs_write):
            fd = gfapi.GlusterFile(2)
            ret = fd.write("hello")
            self.assertEqual(ret, 5)

    def test_write_binary_success(self):
        mock_glfs_write = Mock()
        mock_glfs_write.return_value = 3

        with patch("gluster.gfapi.api.glfs_write", mock_glfs_write):
            fd = gfapi.GlusterFile(2)
            b = bytearray(3)
            ret = fd.write(b)
            self.assertEqual(ret, 3)

    def test_write_fail_exception(self):
        mock_glfs_write = Mock()
        mock_glfs_write.return_value = -1

        with patch("gluster.gfapi.api.glfs_write", mock_glfs_write):
            fd = gfapi.GlusterFile(2)
            self.assertRaises(OSError, fd.write, "hello")

    def test_fallocate_success(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_fallocate = Mock()
        mock_glfs_fallocate.return_value = 0

        with patch("gluster.gfapi.api.glfs_fallocate", mock_glfs_fallocate):
            fd = gfapi.GlusterFile(2)
            ret = fd.fallocate(0, 0, 1024)
            self.assertEqual(ret, 0)

    def test_fallocate_fail_exception(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_fallocate = Mock()
        mock_glfs_fallocate.return_value = -1

        with patch("gluster.gfapi.api.glfs_fallocate", mock_glfs_fallocate):
            fd = gfapi.GlusterFile(2)
            self.assertRaises(OSError, fd.fallocate, 0, 0, 1024)

    def test_discard_success(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_discard = Mock()
        mock_glfs_discard.return_value = 0

        with patch("gluster.gfapi.api.glfs_discard", mock_glfs_discard):
            fd = gfapi.GlusterFile(2)
            ret = fd.discard(1024, 1024)
            self.assertEqual(ret, 0)

    def test_discard_fail_exception(self):
        raise SkipTest("need to solve issue with dependency on libgfapi.so")
        mock_glfs_discard = Mock()
        mock_glfs_discard.return_value = -1

        with patch("gluster.gfapi.api.glfs_discard", mock_glfs_discard):
            fd = gfapi.GlusterFile(2)
            self.assertRaises(OSError, fd.discard, 1024, 1024)


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

    def setUp(self):
        self._saved_glfs_new = gluster.gfapi.api.glfs_new
        gluster.gfapi.api.glfs_new = _mock_glfs_new

        self._saved_glfs_set_volfile_server = \
            gluster.gfapi.api.glfs_set_volfile_server
        gluster.gfapi.api.glfs_set_volfile_server = \
            _mock_glfs_set_volfile_server

        self._saved_glfs_init = gluster.gfapi.api.glfs_init
        gluster.gfapi.api.glfs_init = _mock_glfs_init

        self._saved_glfs_fini = gluster.gfapi.api.glfs_fini
        gluster.gfapi.api.glfs_fini = _mock_glfs_fini

        self._saved_glfs_close = gluster.gfapi.api.glfs_close
        gluster.gfapi.api.glfs_close = _mock_glfs_close

        self._saved_glfs_closedir = gluster.gfapi.api.glfs_closedir
        gluster.gfapi.api.glfs_closedir = _mock_glfs_closedir

    def tearDown(self):
        gluster.gfapi.api.glfs_new = self._saved_glfs_new
        gluster.gfapi.api.glfs_set_volfile_server = \
            self._saved_glfs_set_volfile_server
        gluster.gfapi.api.glfs_fini = self._saved_glfs_fini
        gluster.gfapi.api.glfs_close = self._saved_glfs_close
        gluster.gfapi.api.glfs_closedir = self._saved_glfs_closedir
        gluster.gfapi.api.glfs_init = self._saved_glfs_init

    def test_creat_success(self):
        mock_glfs_creat = Mock()
        mock_glfs_creat.return_value = 2

        with patch("gluster.gfapi.api.glfs_creat", mock_glfs_creat):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            with vol.creat("file.txt", os.O_WRONLY, 0644) as fd:
                self.assertTrue(isinstance(fd, gfapi.GlusterFile))
                self.assertEqual(mock_glfs_creat.call_count, 1)
                mock_glfs_creat.assert_called_once_with(2,
                                                        "file.txt",
                                                        os.O_WRONLY, 0644)

    def test_creat_fail_exception(self):
        mock_glfs_creat = Mock()
        mock_glfs_creat.return_value = None

        def assert_creat():
            vol = gfapi.GlusterFilesystem("localhost", "test")
            with vol.creat("file.txt", os.O_WRONLY, 0644) as fd:
                self.assertEqual(fd, None)

        with patch("gluster.gfapi.api.glfs_creat", mock_glfs_creat):
            self.assertRaises(OSError, assert_creat)

    def test_getxattr_success(self):
        def mock_glfs_getxattr(fs, path, key, buf, maxlen):
            buf.value = "fake_xattr"
            return 10

        with patch("gluster.gfapi.api.glfs_getxattr", mock_glfs_getxattr):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            buf = vol.getxattr("file.txt", "key1", 32)
            self.assertEquals("fake_xattr", buf)

    def test_getxattr_fail_exception(self):
        mock_glfs_getxattr = Mock()
        mock_glfs_getxattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_getxattr", mock_glfs_getxattr):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(IOError, vol.getxattr, "file.txt", "key1",
                              32)

    def test_listxattr_success(self):
        def mock_glfs_listxattr(fs, path, buf, buflen):
            buf.raw = "key1\0key2\0"
            return 10

        with patch("gluster.gfapi.api.glfs_listxattr", mock_glfs_listxattr):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            xattrs = vol.listxattr("file.txt")
            self.assertTrue("key1" in xattrs)
            self.assertTrue("key2" in xattrs)

    def test_listxattr_fail_exception(self):
        mock_glfs_listxattr = Mock()
        mock_glfs_listxattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_listxattr", mock_glfs_listxattr):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(IOError, vol.listxattr, "file.txt")

    def test_lstat_success(self):
        mock_glfs_lstat = Mock()
        mock_glfs_lstat.return_value = 0

        with patch("gluster.gfapi.api.glfs_lstat", mock_glfs_lstat):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            stat = vol.lstat("file.txt")
            self.assertTrue(isinstance(stat, gfapi.Stat))

    def test_lstat_fail_exception(self):
        mock_glfs_lstat = Mock()
        mock_glfs_lstat.return_value = -1

        with patch("gluster.gfapi.api.glfs_lstat", mock_glfs_lstat):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, vol.lstat, "file.txt")

    def test_mkdir_success(self):
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.return_value = 0

        with patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            ret = vol.mkdir("testdir", 0775)
            self.assertEquals(ret, 0)

    def test_mkdir_fail_exception(self):
        mock_glfs_mkdir = Mock()
        mock_glfs_mkdir.return_value = -1

        with patch("gluster.gfapi.api.glfs_mkdir", mock_glfs_mkdir):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, vol.mkdir, "testdir", 0775)

    def test_open_success(self):
        mock_glfs_open = Mock()
        mock_glfs_open.return_value = 2

        with patch("gluster.gfapi.api.glfs_open", mock_glfs_open):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            with vol.open("file.txt", os.O_WRONLY) as fd:
                self.assertTrue(isinstance(fd, gfapi.GlusterFile))
                self.assertEqual(mock_glfs_open.call_count, 1)
                mock_glfs_open.assert_called_once_with(2,
                                                       "file.txt",
                                                       os.O_WRONLY)

    def test_open_fail_exception(self):
        mock_glfs_open = Mock()
        mock_glfs_open.return_value = None

        def assert_open():
            with vol.open("file.txt", os.O_WRONLY) as fd:
                self.assertEqual(fd, None)

        with patch("gluster.gfapi.api.glfs_open", mock_glfs_open):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, assert_open)

    def test_opendir_success(self):
        mock_glfs_opendir = Mock()
        mock_glfs_opendir.return_value = 2

        with patch("gluster.gfapi.api.glfs_opendir", mock_glfs_opendir):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            d = vol.opendir("testdir")
            self.assertTrue(isinstance(d, gfapi.GlusterDir))

    def test_opendir_fail_exception(self):
        mock_glfs_opendir = Mock()
        mock_glfs_opendir.return_value = None

        with patch("gluster.gfapi.api.glfs_opendir", mock_glfs_opendir):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, vol.opendir, "testdir")

    def test_rename_success(self):
        mock_glfs_rename = Mock()
        mock_glfs_rename.return_value = 0

        with patch("gluster.gfapi.api.glfs_rename", mock_glfs_rename):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            ret = vol.rename("file.txt", "newfile.txt")
            self.assertEquals(ret, 0)

    def test_rename_fail_exception(self):
        mock_glfs_rename = Mock()
        mock_glfs_rename.return_value = -1

        with patch("gluster.gfapi.api.glfs_rename", mock_glfs_rename):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, vol.rename, "file.txt",
                              "newfile.txt")

    def test_rmdir_success(self):
        mock_glfs_rmdir = Mock()
        mock_glfs_rmdir.return_value = 0

        with patch("gluster.gfapi.api.glfs_rmdir", mock_glfs_rmdir):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            ret = vol.rmdir("testdir")
            self.assertEquals(ret, 0)

    def test_rmdir_fail_exception(self):
        mock_glfs_rmdir = Mock()
        mock_glfs_rmdir.return_value = -1

        with patch("gluster.gfapi.api.glfs_rmdir", mock_glfs_rmdir):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, vol.rmdir, "testdir")

    def test_unlink_success(self):
        mock_glfs_unlink = Mock()
        mock_glfs_unlink.return_value = 0

        with patch("gluster.gfapi.api.glfs_unlink", mock_glfs_unlink):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            ret = vol.unlink("file.txt")
            self.assertEquals(ret, 0)

    def test_unlink_fail_exception(self):
        mock_glfs_unlink = Mock()
        mock_glfs_unlink.return_value = -1

        with patch("gluster.gfapi.api.glfs_unlink", mock_glfs_unlink):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(OSError, vol.unlink, "file.txt")

    def test_setxattr_success(self):
        mock_glfs_setxattr = Mock()
        mock_glfs_setxattr.return_value = 0

        with patch("gluster.gfapi.api.glfs_setxattr", mock_glfs_setxattr):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            ret = vol.setxattr("file.txt", "key1", "hello", 5)
            self.assertEquals(ret, 0)

    def test_setxattr_fail_exception(self):
        mock_glfs_setxattr = Mock()
        mock_glfs_setxattr.return_value = -1

        with patch("gluster.gfapi.api.glfs_setxattr", mock_glfs_setxattr):
            vol = gfapi.GlusterFilesystem("localhost", "test")
            self.assertRaises(IOError, vol.setxattr, "file.txt",
                              "key1", "hello", 5)
