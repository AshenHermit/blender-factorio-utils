import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
from ..classes_manager import CLSManager

from ..info import addon_id, rotator_name
from ..menu_operator import MenuOperator

def get_rotator(context):
    rotator = context.view_layer.objects.get(rotator_name)
    if rotator is None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        rotator = context.view_layer.objects.active
        rotator.name = rotator_name
    return rotator

def reparent_to_rotator(context, object, reset_rotation=True):
    rotator = get_rotator(context)
    if reset_rotation:
        rotator.rotation_euler = (0,0,0)
    
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    context.view_layer.objects.active = rotator
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)