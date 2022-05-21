import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
import math

from ..menu_operator import MenuOperator

from ..classes_manager import CLSManager
from . import utils_rotator

from ..info import addon_id

@CLSManager.reg_bpy_class
class FactorioUtils_SetupEnvironment(MenuOperator):
    bl_idname = f"factorio.setup_environment"
    bl_label = "Factorio Utils: Setup Environment"
    bl_description = "Sets up lighting: creates sun"
    bl_category = "Object"
    bl_options = {"REGISTER",}

    def setup_light(self, context):
        # delete existing light
        light = bpy.context.view_layer.objects.get("Light")
        if light is not None:
            bpy.ops.object.select_all(action='DESELECT')
            light.select_set(True)
            bpy.ops.object.delete()

        bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        sun = context.view_layer.objects.active
        sun.name = "sun"
        sun.location.xyz = (0,0,-4.0)
        sun.rotation_euler = (math.pi/4.0, 0, math.pi + math.pi/4)
        sun.data.energy = 10.0

        context.view_layer.objects.active = sun
        utils_rotator.reparent_to_rotator(context, sun)

    def execute(self, context):
        bpy.ops.ed.undo_push()
        self.setup_light(context)
        return {"FINISHED"}
