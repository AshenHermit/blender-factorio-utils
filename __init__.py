import importlib, sys
from .install_requirements import install_requirements
install_requirements()

import bpy, os
from . import factorio_utils
from . import operators
from . import progress_bars
from pathlib import Path

from .classes_manager import CLSManager

# Python doesn't reload package sub-modules at the same time as __init__.py!
CFD = Path(__file__).parent.resolve()
for file in CFD.rglob("*.py"):
    if str(file.resolve()) == str(Path(__file__).resolve()): continue
    module_name = file.with_suffix("").relative_to(CFD).as_posix().replace("/", ".")
    module_name = module_name.replace(".__init__", "")
    module_name = f"{__name__}.{module_name}"
    module = sys.modules.get(module_name)
    if module: importlib.reload(module)

# clear out any scene update funcs hanging around, e.g. after a script reload
for collection in [bpy.app.handlers.depsgraph_update_post, bpy.app.handlers.load_post]:
	for func in collection:
		if func.__module__.startswith(__name__):
			collection.remove(func)


bl_info = {
    "name": "Factorio Utils",
    "author": "Ashen Hermit",
    "version": (0, 1),
    "blender": (3, 1, 0),
    "location": "View3D > Tools > Factorio Utils",
    "description": "A set of workflow tools to export graphics to Factorio game.",
    "warning": "WIP",
    "wiki_url": "",
    "category": "Import-Export"
}

def register():
    for progress_agent in progress_bars.progress_agents:
        progress_agent.register()
    
    CLSManager.register()

def unregister():
    CLSManager.unregister()

if __name__ == "__main__":
    register()