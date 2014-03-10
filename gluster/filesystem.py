import gfapi
import osfilesystem as osfs
from urlparse import urlparse


def getfs(urlstring):
    url = urlparse(urlstring)
    if url.scheme == "file":
        return osfs.OSFilesytem()
    if url.scheme == "gluster":
        volid = url.path.split('/', 2)[1]
        return gfapi.GlusterFilesystem(url.hostname, volid)
