import importlib
import sys
import os
import subprocess

from pkg_resources import require

class Requirement():
    def __init__(self, pckg_name, import_name=None) -> None:
        self.pckg_name = pckg_name
        self.import_name = import_name or self.pckg_name

requirements = [
    Requirement("Pillow", "PIL")
]

def install_requirements():
    try:
        for requirement in requirements:
            importlib.import_module(requirement.import_name)
    except:
        python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
        target = os.path.join(sys.prefix, 'lib', 'site-packages')
        print(python_exe)
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        for requirement in requirements:
            subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", requirement.pckg_name, "-t", target])

        have_trouble = False
        for requirement in requirements:
            try:
                module = importlib.import_module(requirement.import_name)
                importlib.reload(module)

            except:
                if not have_trouble: print("####  WAIT A MINUTE  ####")
                have_trouble = True
                print(f"module \"{requirement.pckg_name}\" could not be installed in the Blender python")
            
        if have_trouble:
            print(f"This often happens due to the lack of write permissions to the folder: \n\"{target}\"")
            print(f"You can try running blender with admin rights.")