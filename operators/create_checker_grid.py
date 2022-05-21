import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
import math

from ..menu_operator import MenuOperator
from . import utils_rotator
from ..classes_manager import CLSManager

from ..info import addon_id

@CLSManager.reg_bpy_class
class FactorioUtils_CreateCheckerGrid(MenuOperator):
    bl_idname = f"factorio.create_checker_grid"
    bl_label = "Factorio Utils: Create Checker Grid"
    bl_description = "Creates checker grid plane representing game tiles."
    bl_category = "Object"
    bl_options = {"REGISTER",}

    def create_shadow_catcher_material(self):
        mat_name = "checker_grid"
        mat = bpy.data.materials.get(mat_name)
        if mat is not None: return mat

        # create material
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        mat = bpy.data.materials.get(mat_name)
        mat.shadow_method = "NONE"
        mat.blend_method = 'BLEND'

        # remove all nodes except output material
        for node in mat.node_tree.nodes:
            if type(node) is not bpy.types.ShaderNodeOutputMaterial:
                mat.node_tree.nodes.remove(node)

        # Emission
        material_output = mat.node_tree.nodes.get('Material Output')
        emssn = mat.node_tree.nodes.new('ShaderNodeEmission')
        mat.node_tree.links.new(emssn.outputs[0], material_output.inputs[0])

        # Checker Texture
        tex = mat.node_tree.nodes.new('ShaderNodeTexChecker')
        mat.node_tree.links.new(tex.outputs[0], emssn.inputs[0])
        tex.inputs['Color1'].default_value.foreach_set([0.025186829268932343, 0.025186840444803238, 0.02518686093389988, 1.0])
        tex.inputs['Color2'].default_value.foreach_set([0.049706511199474335, 0.04970654100179672, 0.04970656335353851, 1.0])

        # Add Vector
        vmth = mat.node_tree.nodes.new('ShaderNodeVectorMath')
        mat.node_tree.links.new(vmth.outputs['Vector'], tex.inputs['Vector'])
        vmth.operation = "ADD"
        vmth.inputs[1].default_value.foreach_set([0.5, 0.5, 0.0])

        # Multiply Vector
        vmth_mult = mat.node_tree.nodes.new('ShaderNodeVectorMath')
        mat.node_tree.links.new(vmth_mult.outputs['Vector'], vmth.inputs['Vector'])
        vmth_mult.operation = "MULTIPLY"
        vmth_mult.inputs[1].default_value.foreach_set([8.0, 8.0, 8.0])
        
        # Texture Coordinate
        tcoord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
        mat.node_tree.links.new(tcoord.outputs['UV'], vmth_mult.inputs[0])

        return mat

    def add_shadow_catcher(self, context):
        plane_name = "checker_grid"
        if context.view_layer.objects.get(plane_name) is not None: return
        # create plane
        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        plane = context.view_layer.objects.active
        plane.name = plane_name
        plane.hide_render = True

        # scale plane so it will look normal in isometric view, instead of shrinking vertically
        view_factor = 1.0/math.sin(math.pi/4.0)
        plane.scale.xyz = (20, 20*view_factor, 20)

        # create and apply material
        mat = self.create_shadow_catcher_material()
        plane.active_material = mat

        context.view_layer.objects.active = plane
        utils_rotator.reparent_to_rotator(context, plane)

    def execute(self, context):
        bpy.ops.ed.undo_push()
        self.add_shadow_catcher(context)
        return {"FINISHED"}
