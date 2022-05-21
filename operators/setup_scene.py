import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
from ..classes_manager import CLSManager

from ..info import addon_id, rotator_name
from . import utils_rotator
from ..menu_operator import MenuOperator

@CLSManager.reg_bpy_class
class FactorioUtils_SetupScene(MenuOperator):
    bl_idname = f"factorio.setup_scene"
    bl_label = "Factorio Utils: Setup Scene"
    bl_category = "Object"
    bl_options = {"REGISTER",}
    menu_group="setup_all"

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        rotator = utils_rotator.get_rotator(context)

        bpy.ops.factorio.create_shadow_catcher()
        shadow_catcher = context.view_layer.objects.active
        bpy.ops.factorio.create_checker_grid()
        checker_grid = context.view_layer.objects.active
        bpy.ops.factorio.setup_environment()
        light = context.view_layer.objects.active
        bpy.ops.factorio.setup_rendering()
        camera = context.view_layer.objects.active

        return {"FINISHED"}
