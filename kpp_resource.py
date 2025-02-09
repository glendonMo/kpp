import os
import hashlib

from PyQt5 import QtCore, QtGui

from .kpp_param import KppParam
from .constants import RESOURCE_SIGNATURE_KEYS


class LocalResource:
    """ A resource that has been loaded from disk.
    """
    def __init__(self, path_to_file):
        super(LocalResource, self).__init__()
        self.file = path_to_file
        self._buffer = None

        self._load_from_disk()

    def _load_from_disk(self):
        """Load given file's data into a buffer for processing
        """
        image = QtGui.QImage(self.file)
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        buffer.close()
        self._buffer = buffer

    @property
    def filename(self):
        """Name of file on disk

        :rtype: str
        """
        return os.path.basename(self.file)

    @property
    def name(self):
        """Resource name from file's name

        :rtype: str
        """
        return os.path.splitext(os.path.basename(self.file))[0]

    @property
    def md5sum(self):
        """md5sum from file's data

        :rtype: str
        """
        return hashlib.md5(self._buffer.data()).hexdigest()

    @property
    def type(self):
        """Type or resource

        :rtype: str
        """
        return "brushes"

    @property
    def text(self):
        """File's data as a valid string which can be
        included within a .kpp file

        :rtype: str
        """
        return self._buffer.data().toBase64().data().decode("latin1")

    @property
    def signature(self):
        """ The resource's signature

        :rtype: dict
        """
        return {
            "filename": self.filename,
            "name": self.name,
            "md5sum": self.md5sum,
            "type": self.type,
        }


class KppResource(KppParam):
    """A resource within a .kpp file
    """
    def __init__(self):
        super(KppResource, self).__init__()
        self.param_tag = "resource"
        self.is_local_resource = False
        self._path_to_file = None

    def __getitem__(self, item):
        """Get the value of given item from resource signature values

        :param item: key to get value of
        :type item: str
        :raises KeyError: when given item is not a valid signature key
        """
        if not self._can_add_key_to_signature(item):
            raise KeyError(
                f"Item {item}, is not a valid resource signature value")

        return super(KppResource, self).__getitem__(item)

    def __setitem__(self, key, value):
        """Set the value of given key to given value

        :param key: key to used for given value
        :type key: str
        :param value: value to used for given key
        :type key: any
        :raises KeyError: when given item is not a valid signature key
        :raises FileExistsError: when resource represents a file on disk
        """
        if self.is_local_resource:
            raise FileExistsError("Cannot change a resource loaded from disk.")

        if not self._can_add_key_to_signature(key):
            raise KeyError(
                f"Key {key}, is not a valid resource signature value")

        super(KppResource, self).__setitem__(key, value)

    def _can_add_key_to_signature(self, key):
        """Check whether given key is a valid resource signature key

        :param key: key to check
        :type key: str
        :rtype: bool
        """
        return key in RESOURCE_SIGNATURE_KEYS

    @property
    def file(self):
        """Get the file on disk that this resource represents

        :rtype: str
        """
        return self._path_to_file

    @file.setter
    def file(self, path_to_file):
        """Set this resource to represent a file on disk
        This makes the resource read only as it does not
        change the file on disk.

        :raises FileNotFoundError: when given path_to_file does not exist
        """
        if not os.path.exists(path_to_file):
            raise FileNotFoundError(f"File {path_to_file}, does not exist.")

        local_resource = LocalResource(path_to_file)

        self["filename"] = local_resource.filename
        self["name"] = local_resource.name
        self["md5sum"] = local_resource.md5sum
        self["type"] = local_resource.type
        self.value = local_resource.text

        self.is_local_resource = True
        self._path_to_file = path_to_file
