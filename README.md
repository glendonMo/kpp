# kpp 

The `kpp` module offers an interface for interacting with and creating
.kpp files that, once saved, can be loaded into Krita as a valid brush preset. 

[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## Brief overview of the .kpp file format
".kpp files are PNGs which contain an annotation with the XML data for the brush engine" [(quote from the Krita documentation.)](https://docs.krita.org/en/reference_manual/resource_management/paintoppresets.html)
For my purposes, I wanted to be able to create a .kpp file programmatically using any random image without needing to open Krita.

This is where `kpp` comes in. `kpp` allows for an existing .kpp file to be read and modified outside of Krita. Once saved, the resulting `.kpp` file can be loaded into Krita as a valid brush preset.

Like the Krita documentation mentions, a `.kpp` file is a PNG which has been annotated with XML data. There are a ton of brush settings within this data. To keep this to the point, we will focus on the settings that are important for loading a custom image into Krita as a brush preset.

The XML data stored within a .kpp file has one root element called `Preset`. The `Preset` element has a `resources` child and various `param` children. When an image is added to a .kpp file, it is stored as a child of the `resources` attribute. The value of a `resource` is the image as a byte array which has been decoded as `latin_1`.

A md5 checksum is generated using the contents of the given image and is referenced in the `brush_definition` parameter.


Here is a botched example of what that looks like:
```xml
<Preset name="a) cool brush name" embedded_resources="1" paintopid="paintbrush">
    <resouces>
        <resource name="cool_image" md5sum="generated from file contents" filename="cool_image.png" type="brushes">
            byte array decoded as latin_1
        </resource>
    </resouces>
    <param name="cool param" type="string">cool</param>
    ...
    <param name="brush_definition" type="string">&lt;Brush ... md5sum="must match md5sum in corresponding resource attribute" filename="cool_image.png" ...&gt;</param>
    ...
</Preset>
```

## Requirements
- Python: **3.8** or later
- PyQt5: **5.15.2** or later

## Recommended usage
It is recommended to start from a existing .kpp file. You can then tweak the parameters to your liking.

> **Note**
> The brush angle in a brush preset is represented as radians instead of degrees.
> The brush scale is a percentage which is derived from the minimum and maximum brush sizes at the time the preset was saved.
```python
from kpp import Kpp

kpp_file = r"path\to\kpp_file.kpp"

_kpp = Kpp.from_kpp(kpp_file)

# set kpp parameters
_kpp["name"] = "b) " + "cool_brush"
_kpp["paintopid"] = "paintbrush"
_kpp.filename = _kpp["name"]

# initialize resource as a local resource
# this makes the resource read only!
_kpp.resource.file = r"path\to\png_file.png"

# set brush parameters
_kpp.parameters["EraserMode"] = False
_kpp.parameters["brush_definition"].md5sum = _kpp.resource["md5sum"]
_kpp.parameters["brush_definition"].filename = _kpp.resource["filename"]
_kpp.parameters["brush_definition"].type = "png_brush"
_kpp.parameters["brush_definition"].angle = math.radians(30)
_kpp.parameters["brush_definition"].scale = 0.5

# add the preview image to the brush definition
preview_image = QtGui.QImage(_kpp.resource.file)
_kpp.preview = preview_image.scaled(
    200,
    200,
    QtCore.Qt.AspectRatioMode.KeepAspectRatio
)

# save the .kpp file to the given directory
saved_kpp_file = _kpp.save(directory)
```
