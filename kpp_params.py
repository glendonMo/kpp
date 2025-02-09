from .kpp_param import KppParam


class KppParams:
    """A group of parameters within a .kpp file
    """
    def __init__(self):
        self._params = []

    def __getitem__(self, item):
        """Get the value of parameter that has the name of item

        :param item: name of parameter to get value of
        :type item: str
        """
        for param in self._params:
            if "name" not in param.params.keys():
                continue
            if not param.params["name"] == item:
                continue
            return param

    def __setitem__(self, key, value):
        """Set the value of parameter that has the name of key to given value

        :param key: name of parameter to set value of
        :type key: str
        :param value: value to used for given parameter
        :type key: any
        """
        for param in self._params:
            if "name" not in param.params.keys():
                continue
            if not param.params["name"] == key:
                continue
            param.value = value

    def __iter__(self):
        """Yield paramters. Enables iteration for this class

        :yield: A given parameter
        :rtype: kpp.KppParam
        """
        yield from self._params

    def __len__(self):
        """Amount of parameters

        :rtype: int
        """
        return len(self._params)

    def append(self, item):
        """Add given parameter

        :param item: paramter to add
        :type item: kpp.KppParam
        :raises TypeError: when given item is not of type kpp.KppParam
        """
        if not isinstance(item, KppParam):
            raise TypeError("item must be of type KppParam.")
        self._params.append(item)

    def clear(self):
        """Remove all params
        """
        del self._params[:]
