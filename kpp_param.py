from xml.etree import ElementTree


class KppParam:
    """A given parameter within a .kpp file
    """
    def __init__(self):
        self._param_values = {}
        self._value = ""
        self.param_tag = "param"

    def __getitem__(self, item):
        """Get the value of given item from paramter values

        :param item: key to get value of
        :type item: str
        """
        return self._param_values[item]

    def __setitem__(self, key, value):
        """Set the value of given key to given value

        :param key: key to used for given value
        :type key: str
        :param value: value to used for given key
        :type key: any
        """
        self._param_values[key] = value

    def __repr__(self):
        """String representation of KppParam

        :rtype: str
        """
        name = self.__class__.__name__
        _values = " ".join(
            f"{key}={value}" for key, value in self._param_values.items())

        _string = f"<{name} {self.param_tag} {_values}>" +\
            f" {self.value} </{name} {self.param_tag}>"
        return _string

    @property
    def params(self):
        """Get the set paramters values

        :rtype: dict
        """
        return self._param_values

    @property
    def value(self):
        """Get the text value of param

        :rtype: any
        """
        return self._value

    @value.setter
    def value(self, value):
        """Set the text value of param

        :param value: new value
        :type value: any
        """
        self._value = value

    def as_element(self):
        """Get KppParam as a xml element

        :rtype: xml.etree.ElementTree.Element
        """
        element = ElementTree.Element(self.param_tag)
        for key, value in self._param_values.items():
            element.set(key, value)
        element.text = self.value
        return element
