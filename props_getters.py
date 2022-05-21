from pathlib import Path
import bpy

class SpritesheetPathException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("spritesheet output path is not specified", *args)

class PropsManager():
    def __init__(self) -> None:
        pass

    @property
    def spritesheet_output_path(self)->Path:
        proj_dir = Path(bpy.data.filepath).parent.as_posix()+"/"
        if not bpy.context.view_layer.factorio.output_path:
            raise SpritesheetPathException()
        output_file_prop = Path(bpy.context.view_layer.factorio.output_path.replace("//", proj_dir))
        return output_file_prop

props_manager = PropsManager() 