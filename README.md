[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg?style=flat-square)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=LWF3MAPZNPDQU&source=url)
# Clarisse Survival Kit

![Header Image](http://remuno.nl/wp-content/uploads/2019/01/mountain_cave.jpg)

>Clarisse Survival Kit(***CSK***) is a set of Python functions for Clarisse to automate repetitive processes such as importing generic textures, Megascans assets and mixing materials.

## Installation

CSK requires Python 2.7 to be installed.

If you have pip installed you can download or link directly to the tarball in the dist folder and use the following command to set it up:

**NOTICE:** OSX users should open their **clarisse.env** file and locate their Python installation before running one of the following commands. The commands must be run with the Python installation that is used by Clarisse.

```sh
$ pip install .\clarisse_survival_kit-0.0.1.tar.gz
```

Otherwise download the zip by clicking the big green button, extract the files and run the following command via the command line:
```sh
$ python setup.py install
```

The shelf will automatically be updated and backed up. If the installation does not install the shelf correctly you can find a shelf_installation.log file in your Isotropix/VERSION/ user folder.

On Windows you can find the shelf_installation.log file here:

>C:/Users/**YOUR_USERNAME**/AppData/Roaming/Isotropix/Clarisse/**VERSION**

On Linux you can find it here:

>/home/**YOUR_USERNAME**/.isotropix/**VERSION**

On Mac you can find it here:

>/Users/**YOUR_USERNAME**/Library/Preferences/Isotropix/Clarisse/**VERSION**


## Features
*When a script asks you to select a material either select the PhysicalStandard material or its parent context*

The kit provides the following scripts:
### Import Asset
  - Import a Megascans asset. Meshes will automatically have their materials assigned when imported as .obj. Alembic(.abc) files will be imported as references. 3D assets such as  3d models, plants & atlases will also have a shading rule created for them. 
  - Import generic textures such as Substance. You can specify which textures should be interpreted as sRGB if needed. Custom rules can be added/modified in the settings.py file.

### Mix Surface
 - Creates a PhysicalBlend material from two specified materials(PhysicalStandard or PhysicalBlend). 
 - Masking features:
   * Height blend: Mixes the materials based on Y elevation. Handy for shore lines.
   * Displacement blend: Checks which displacement map has higher elevation than the other. You can invert the selector or add both layers on top of each other.
   * Slope blend: Mixes two materials based on slope angle. 
   * Triplanar blend: Uses triplanar mapping for the mask. By default the top facing(Y+) angle is masked.
   * Scope blend: A scope object is automatically created to quickly mask things out with a slope
   * Occlusion blend: You can use Ambient Occlusion to blend the materials. Has a huge impact on performance when used with Displacement.
   * Fractal blend: If any other selectors are active the Fractal blend selector will be overlayed on top to break up the masking in the transition areas.

### Replace Surface
You can quickly replace the selected surface or change the mapping settings. If you're replacing a material that was used in a surface mix it will also update.

### Toggle Surface Complexity
Swaps out the selected material temporarily with a simple PhysicalDiffuse material. When you rerun the command on the selected PhysicalStandard material or its parent context it converts it back to the original state.

### Moisten Surface
Adds a wet layer on top of the selected material. Several masking options are available.

### Tint Surface
Adds a blend texture which can be used to colorize the selected surface so it matches better with other surfaces.

### Texture(s) to Triplanar
Converts the selected textures to triplanar.

### Blur Selected Texture(s)
Blurs the selected texture with a custom radius.

# TODO
- Mix Multiple Surfaces. Handy for covering multiple materials simultaneously with one material.
- Scatter point cloud on selected geo. The point cloud will be decimated with the same selectors as used in the Mix Surfaces command except Displacement.
- Import Megascans library GUI. The function is already done and works. It just needs a GUI. You can run it from the script editor if needed.
```python
from clarisse_survival_kit.app import *

import_ms_library("PATH TO THE DOWNLOADED FOLDER", skip_categories=[], ix=ix)
```

if you want to exclude categories you can run the following command. "surfaces" is the name of the custom mixer surfaces.
```python
from clarisse_survival_kit.app import *
import_ms_library("PATH TO THE DOWNLOADED FOLDER", skip_categories=["3d", "3dplant", "atlas", "surface", "surfaces"], ix=ix)
```

Got any ideas? Did I miss anything important? Let me know.

# Thank you
[Aleks Katunar](https://github.com/ddesmond) was really kind to help me test out the script and for becoming a collaborator.

***Isotropix*** for their support and for creating Clarisse.

# License
GNU GPLV3
