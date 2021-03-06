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
import os
import types
import loremipsum

from gluster import gfapi


class BinFileOpsTest(unittest.TestCase):

    vol = None
    path = None
    data = None

    @classmethod
    def setUpClass(cls):
        cls.vol = gfapi.Volume("gfshost", "test")
        cls.vol.set_logging("/dev/null", 7)
        cls.vol.mount()

    @classmethod
    def tearDownClass(cls):
        cls.vol = None

    def setUp(self):
        self.data = bytearray([(k % 128) for k in range(0, 1024)])
        self.path = self._testMethodName + ".io"
        with self.vol.creat(self.path, os.O_WRONLY | os.O_EXCL, 0644) as fd:
            fd.write(self.data)

    def test_bin_open_and_read(self):
        with self.vol.open(self.path, os.O_RDONLY) as fd:
            self.assertTrue(isinstance(fd, gfapi.File))
            buf = fd.read(len(self.data))
            self.assertFalse(isinstance(buf, types.IntType))
            self.assertEqual(buf, self.data)


class FileOpsTest(unittest.TestCase):

    vol = None
    path = None
    data = None

    @classmethod
    def setUpClass(cls):
        cls.vol = gfapi.Volume("gfshost", "test")
        cls.vol.set_logging("/dev/null", 7)
        cls.vol.mount()

    @classmethod
    def tearDownClass(cls):
        cls.vol = None

    def setUp(self):
        self.data = loremipsum.get_sentence()
        self.path = self._testMethodName + ".io"
        with self.vol.creat(self.path, os.O_WRONLY | os.O_EXCL, 0644) as fd:
            rc = fd.write(self.data)
            self.assertEqual(rc, len(self.data))

    def tearDown(self):
        self.path = None
        self.data = None

    def test_open_and_read(self):
        with self.vol.open(self.path, os.O_RDONLY) as fd:
            self.assertTrue(isinstance(fd, gfapi.File))
            buf = fd.read(len(self.data))
            self.assertFalse(isinstance(buf, types.IntType))
            self.assertEqual(buf.value, self.data)

    def test_exists(self):
        e = self.vol.exists(self.path)
        self.assertTrue(e)

    def test_exists_false(self):
        e = self.vol.exists("filedoesnotexist")
        self.assertFalse(e)

    def test_getsize(self):
        size = self.vol.getsize(self.path)
        self.assertEqual(size, len(self.data))

    def test_isfile(self):
        isfile = self.vol.isfile(self.path)
        self.assertTrue(isfile)

    def test_isdir_false(self):
        isdir = self.vol.isdir(self.path)
        self.assertFalse(isdir)

    def test_symlink(self):
        link = self._testMethodName + ".link"
        ret = self.vol.symlink(self.path, link)
        self.assertEqual(ret, 0)
        islink = self.vol.islink(link)
        self.assertTrue(islink)

    def test_islink_false(self):
        islink = self.vol.islink(self.path)
        self.assertFalse(islink)

    def test_lstat(self):
        sb = self.vol.lstat(self.path)
        self.assertFalse(isinstance(sb, types.IntType))
        self.assertEqual(sb.st_size, len(self.data))

    def test_rename(self):
        newpath = self.path + ".rename"
        ret = self.vol.rename(self.path, newpath)
        self.assertEqual(ret, 0)
        self.assertRaises(OSError, self.vol.lstat, self.path)

    def test_stat(self):
        sb = self.vol.stat(self.path)
        self.assertFalse(isinstance(sb, types.IntType))
        self.assertEqual(sb.st_size, len(self.data))

    def test_unlink(self):
        ret = self.vol.unlink(self.path)
        self.assertEqual(ret, 0)
        self.assertRaises(OSError, self.vol.lstat, self.path)

    def test_xattr(self):
        key1, key2 = "hello", "world"
        ret1 = self.vol.setxattr(self.path, "trusted.key1", key1, len(key1))
        self.assertEqual(ret1, 0)
        ret2 = self.vol.setxattr(self.path, "trusted.key2", key2, len(key2))
        self.assertEqual(ret2, 0)

        xattrs = self.vol.listxattr(self.path)
        self.assertFalse(isinstance(xattrs, types.IntType))
        self.assertEqual(xattrs, ["trusted.key1", "trusted.key2"])

        buf = self.vol.getxattr(self.path, "trusted.key1", 32)
        self.assertFalse(isinstance(buf, types.IntType))
        self.assertEqual(buf, "hello")

        ret3 = self.vol.removexattr(self.path, "trusted.key1")
        self.assertEqual(ret3, 0)

        xattrs = self.vol.listxattr(self.path)
        self.assertFalse(isinstance(xattrs, types.IntType))
        self.assertEqual(xattrs, ["trusted.key2"])


class DirOpsTest(unittest.TestCase):

    data = None
    dir_path = None
    file_path = None
    testfile = None

    @classmethod
    def setUpClass(cls):
        cls.vol = gfapi.Volume("gfshost", "test")
        cls.vol.set_logging("/dev/null", 7)
        cls.vol.mount()
        cls.testfile = "testfile.io"

    @classmethod
    def tearDownClass(cls):
        cls.vol = None
        cls.testfile = None

    def setUp(self):
        self.data = loremipsum.get_sentence()
        self.dir_path = self._testMethodName + "_dir"
        self.vol.mkdir(self.dir_path, 0755)
        self.file_path = self.dir_path + "/" + self.testfile
        with self.vol.creat(
                self.file_path, os.O_WRONLY | os.O_EXCL, 0644) as fd:
            rc = fd.write(self.data)
            self.assertEqual(rc, len(self.data))

    def tearDown(self):
        self.dir_path = None
        self.file_path = None
        self.data = None

    def test_isdir(self):
        isdir = self.vol.isdir(self.dir_path)
        self.assertTrue(isdir)

    def test_isfile_false(self):
        isfile = self.vol.isfile(self.dir_path)
        self.assertFalse(isfile)

    def test_dir_listing(self):
        fd = self.vol.opendir(self.dir_path)
        self.assertTrue(isinstance(fd, gfapi.Dir))
        files = []
        while True:
            ent = fd.next()
            if not isinstance(ent, gfapi.Dirent):
                break
            name = ent.d_name[:ent.d_reclen]
            files.append(name)
        self.assertEqual(files, [".", "..", self.testfile])

    def test_delete_file_and_dir(self):
        ret = self.vol.unlink(self.file_path)
        self.assertEqual(ret, 0)
        self.assertRaises(OSError, self.vol.lstat, self.file_path)

        ret = self.vol.rmdir(self.dir_path)
        self.assertEqual(ret, 0)
        self.assertRaises(OSError, self.vol.lstat, self.dir_path)
