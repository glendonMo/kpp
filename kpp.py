import os
from xml.etree import ElementTree

from PyQt5 import QtGui

from .constants import KPP_ACCEPTED_ROOT_KEYS
from .kpp_param import KppParam
from .kpp_params import KppParams
from .kpp_resource import KppResource
from .kpp_brush import KppBrush


class Kpp:
    """The .kpp file as a class
    """
    def __init__(self, filename, preview=None):
        self._extension = ".kpp"
        self._root = KppParam()
        self._root.param_tag = "Preset"
        self._preview = preview
        self.filename = filename
        self.parameters = KppParams()
        self.resource = KppResource()

    def __getitem__(self, item):
        """Get root level Kpp values

        :rtype: any
        """
        return self._root[item]

    def __setitem__(self, key, value):
        """Set root level Kpp values
        These values are used in the root element of the .kpp file

        :param key: key to used for given value
        :type key: str
        :param value: value to used for given key
        :type value: any
        """
        if key not in KPP_ACCEPTED_ROOT_KEYS:
            raise ValueError(
                f"{key}, is not a supported key within a .kpp root element." +
                f"\nAccepted keys are: {KPP_ACCEPTED_ROOT_KEYS}"
            )
        self._root[key] = value

    def __len__(self):
        """Amount of parameters

        :rtype: int
        """
        return len(self.parameters)

    def __repr__(self):
        """String representation of Kpp

        :rtype: str
        """
        return f"<kpp.Kpp object at {hex(self.__hash__())}>"

    @property
    def preview(self):
        """Get Kpp preview image

        :rtype: QtGui.QImage
        """
        return self._preview

    @preview.setter
    def preview(self, image):
        """Set Kpp preview image
        This is the file used within Krita as the brush thumbnail

        :param image: image to use as the brush preview
        :type image: QtGui.QImage
        :raises TypeError: when given image is not of type QtGui.QImage
        """
        if not isinstance(image, QtGui.QImage):
            raise TypeError("Kpp.preview must be of type QtGui.QImage.")
        self._preview = image

    @property
    def version(self):
        """Get the Kpp verions which can be used to set the
        version value within the .kpp file

        :rtype: float
        """
        return 5.0

    @property
    def preset(self):
        """Get Kpp as a xml string which can be used to set the
        preset value within the .kpp file

        :rtype: str
        """
        return self.to_xml()

    def to_element(self):
        """Get Kpp definition as a xml element

        :rtype: xml.etree.ElementTree.Element
        """
        root = self._root.as_element()
        resources = ElementTree.Element("resources")
        resources.append(self.resource.as_element())
        root.append(resources)

        for param in self.parameters:
            root.append(param.as_element())
        return root

    def to_xml(self):
        """Get the current Kpp defintion as a xml string

        :rtype: str
        """
        return ElementTree.tostring(self.to_element(), encoding='unicode')

    @classmethod
    def from_xml(cls, xml_string):
        """Instantiate a Kpp class using the given xml

        :param xml_string: valid xml as a string
        :type xml_string: str
        """
        root = ElementTree.fromstring(xml_string)
        kpp = cls(root.get("name"))

        # set root item values
        for key, value in root.items():
            kpp[key] = value

        # add params to
        for param in root:
            if param.tag == "resources":
                # TODO(glendon): If multiple resources are a possiblity,
                # then this should change to support that.
                resource = [
                    element
                    for element in param.iter()
                    if element is not param
                ]

                if not resource:
                    continue

                # isolate resource parameter
                resource = resource[0]
                kpp.resource.param_tag = resource.tag
                kpp.resource.value = resource.text
                for key, value in resource.items():
                    kpp.resource[key] = value
                continue

            kpp_param = KppParam()
            kpp_param.param_tag = param.tag
            kpp_param.value = param.text
            for key, value in param.items():
                kpp_param[key] = value

            # override brush_definition parameter
            # TODO(glendon): I don't like this way of doing this.
            # There should be a cleaner way.
            if kpp_param["name"] == "brush_definition":
                kpp_brush = KppBrush.from_definition_string(kpp_param.value)
                kpp_brush.param_tag = kpp_param.param_tag
                for key, value in param.items():
                    kpp_brush[key] = value
                kpp_param = kpp_brush

            kpp.parameters.append(kpp_param)

        return kpp

    @classmethod
    def from_kpp(cls, path_to_kpp_file):
        """Instantiate a Kpp class using the given kpp file

        :param path_to_kpp_file: absolute path to kpp file on disk
        :type path_to_kpp_file: str
        :return: the given kpp file as a Kpp instance
        :rtype: kpp.Kpp
        """
        kpp_image = QtGui.QImage(path_to_kpp_file)
        kpp = cls.from_xml(kpp_image.text("preset"))
        return kpp

    def save(self, save_dir):
        """Save Kpp to a directory on disk

        :param save_dir: the direcroty to save to
        :type save_dir: str
        :raises ValueError: when a preview is not set, a filename is not set,
            and the directory to save the kpp file within, does not exist
        :return: path to saved kpp file on disk
        :rtype: str
        """
        if not self.preview:
            raise ValueError("Cannot save .kpp file without a preview image.")

        if not self.filename:
            raise ValueError("Cannot save .kpp file with empty filename.")

        if not os.path.exists(save_dir):
            raise FileNotFoundError(
                f"The directory {save_dir}, does not exist")

        save_png_path = os.path.join(save_dir, self.filename + ".png")
        save_kpp_path = save_png_path.replace(".png", self._extension)

        self.preview.setText("preset", self.preset)
        self.preview.setText("version", str(self.version))
        self.preview.save(save_png_path)

        if os.path.exists(save_kpp_path):
            os.remove(save_kpp_path)

        os.rename(save_png_path, save_kpp_path)

        return save_kpp_path
