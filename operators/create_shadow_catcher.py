import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
from . import utils_rotator
from ..menu_operator import MenuOperator
from ..classes_manager import CLSManager

from ..info import addon_id

@CLSManager.reg_bpy_class
class FactorioUtils_CreateShadowCatcher(MenuOperator):
    bl_idname = f"factorio.create_shadow_catcher"
    bl_label = "Factorio Utils: Create Shadow Catcher"
    bl_description = "Creates shadow catcher plane"
    bl_category = "Object"
    bl_options = {"REGISTER",}

    def create_shadow_catcher_material(self):
        mat_name = "shadow_catcher"
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

        ## for Eevee
        # Principled BSDF
        material_output = mat.node_tree.nodes.get('Material Output')
        material_output.target = "EEVEE"
        bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(bsdf.outputs[0], material_output.inputs[0])
        bsdf.inputs['Base Color'].default_value.foreach_set([0,0,0,1])
        bsdf.inputs['Roughness'].default_value = 1.0
        bsdf.inputs['Specular'].default_value = 0.0

        # Color Ramp
        ramp = mat.node_tree.nodes.new('ShaderNodeValToRGB')
        mat.node_tree.links.new(ramp.outputs['Color'], bsdf.inputs['Alpha'])
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color.foreach_set([1,1,1,1])
        ramp.color_ramp.elements[1].position = 0.15454579889774323
        ramp.color_ramp.elements[1].color.foreach_set([0,0,0,1])

        # Shader to RGB
        s2rgb = mat.node_tree.nodes.new('ShaderNodeShaderToRGB')
        mat.node_tree.links.new(s2rgb.outputs['Color'], ramp.inputs['Fac'])

        # Diffuse BSDF
        dfs = mat.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        mat.node_tree.links.new(dfs.outputs[0], s2rgb.inputs[0])
        dfs.inputs['Color'].default_value.foreach_set([1,1,1,1])
        dfs.inputs['Roughness'].default_value = 1.0

        ## for Cycles
        # Output Material node and Principled BSDF
        material_output = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        material_output.target = "CYCLES"
        bsdf = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        mat.node_tree.links.new(bsdf.outputs[0], material_output.inputs[0])
        bsdf.inputs['Base Color'].default_value.foreach_set([1,1,1,1])
        bsdf.inputs['Roughness'].default_value = 1.0
        bsdf.inputs['Specular'].default_value = 0.0
        bsdf.inputs['Alpha'].default_value = 0.8

        return mat

    def add_shadow_catcher(self, context):
        plane_name = "shadow_catcher"
        if context.view_layer.objects.get(plane_name) is not None: return
        # create plane
        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        plane = context.view_layer.objects.active
        plane.name = plane_name
        plane.scale.xyz = (50,50,50)

        # add shadow catcher material
        mat = self.create_shadow_catcher_material()
        plane.active_material = mat

        # for cycles
        plane.is_shadow_catcher = True
        context.view_layer.objects.active = plane
        utils_rotator.reparent_to_rotator(context, plane)

    def execute(self, context):
        bpy.ops.ed.undo_push()
        self.add_shadow_catcher(context)
        return {"FINISHED"}
