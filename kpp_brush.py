from .constants import BRUSH_DEFINITION_KEYS, BRUSH_DEFINITION_NAME
from .kpp_param import KppParam


def process_combined_kwargs(combined_kwargs, separator=None):
    """Helper function to split key value pairs from one another
    that have been joined using the given separator

    :param combined_kwargs: key value pairs joined as a string object.
        Example: "name=John;age=35"
    :type combined_kwargs: str
    :param separator: character that splits key value pairs, defaults to None
    :type separator: str, optional
    :return: the split key values pairs as a dictionary object
    :rtype: dict
    """
    separator = separator or " "
    processed_kwargs = {}

    # split kwargs on separator
    combined_kwargs = combined_kwargs.split(separator)

    for combined_kwarg in combined_kwargs:
        if not combined_kwarg:
            continue
        key, value = combined_kwarg.split("=")
        processed_kwargs[key] = value.replace('"', "")

    return processed_kwargs


class KppBrush(KppParam):
    """A brush definition within a .kpp file.
    """
    def __init__(self):
        super(KppBrush, self).__init__()

        self.autoSpacingCoeff = None
        self.useAutoSpacing = None
        self.angle = None
        self.md5sum = None
        self.filename = None
        self.AdjustmentMidPoint = None
        self.ContrastAdjustment = None
        self.spacing = None
        self.AdjustmentVersion = None
        self.ColorAsMask = None
        self.type = None
        self.scale = None
        self.AutoAdjustMidPoint = None
        self.brushApplication = None

    @classmethod
    def from_definition_string(cls, string):
        """Initialize a KppBrush instance using an exist brush definition

        :param string: existing brush definition
        :type string: str
        :rtype: kpp.KppBrush
        """
        # remove tag
        string = string.replace("<Brush", "").replace("/>", "")
        # split kwargs from one another
        split_kwargs = process_combined_kwargs(string)
        # set kwargs values on class
        kpp_brush = cls()
        for key in BRUSH_DEFINITION_KEYS:
            setattr(kpp_brush, key, split_kwargs[key])
        return kpp_brush

    def to_defintion_string(self):
        """Use class attributes to construct a a brush definition string

        :return: a valid brush definition string.
        :rtype: str
        """
        attributes_as_strings = []
        for key in BRUSH_DEFINITION_KEYS:
            value = getattr(self, key)
            attributes_as_strings.append(f'{key}="{str(value)}"')

        string = " ".join(attributes_as_strings)
        return f"<Brush {string}/>"

    @property
    def params(self):
        """Get the set parameter values

        :rtype: dict
        """
        # name should always be brush_definition
        self._param_values["name"] = BRUSH_DEFINITION_NAME
        return self._param_values

    @property
    def value(self):
        """Get brush definition string

        :rtype: str
        """
        # only return definition string as value
        return self.to_defintion_string()
