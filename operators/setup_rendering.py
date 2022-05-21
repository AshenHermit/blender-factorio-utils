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
class FactorioUtils_SetupRendering(MenuOperator):
    bl_idname = f"factorio.setup_rendering"
    bl_label = "Factorio Utils: Setup Rendering"
    bl_description = "Sets up the orthographic camera and sets a few rendering settings (film_transparent, resolution)"
    bl_category = "Object"
    bl_options = {"REGISTER",}
    
    def setup_camera(self, context):
        # create camera if not exists
        camera = bpy.context.view_layer.objects.get("Camera")
        if camera is None:
            bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(0,0,0), scale=(1, 1, 1))
            camera = context.view_layer.objects.active

        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = 8.0
        camera.data.clip_end = 200.0

        camera.location.xyz = (0, -60, 60)
        camera.rotation_euler = (math.pi/4, 0, 0)
        context.view_layer.objects.active = camera
        utils_rotator.reparent_to_rotator(context, camera)

    def setup_rendering(self, context):
        context.scene.render.resolution_x = 256
        context.scene.render.resolution_y = 256
        context.scene.render.resolution_percentage = 100

        context.scene.render.film_transparent = True
        context.scene.render.filter_size = 1.5

    def execute(self, context):
        bpy.ops.ed.undo_push()
        self.setup_rendering(context)
        self.setup_camera(context)
        return {"FINISHED"}
