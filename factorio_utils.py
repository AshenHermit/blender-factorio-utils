#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

import argparse
from functools import partial
import os
import sys
import traceback
import importlib
import bpy
import bmesh
import addon_utils
from bpy_extras.io_utils import ImportHelper
from .classes_manager import CLSManager

from .info import addon_id
from . import progress_bars, operators

@CLSManager.reg_prop_group(bpy.types.Scene, "factorio")
class FactorioUtils_SceneProps(bpy.types.PropertyGroup):
    active_object: bpy.props.PointerProperty(
        name="Main object",
        description="Object, animations of which must be rendered.",
        type=bpy.types.Object,
    )
    directions_count: bpy.props.IntProperty(
        name="Directions count",
        description="Count of view directions to render scene in.",
        min=1,
        soft_max=8,
        default=1,
    )
    render_hr_versions: bpy.props.BoolProperty(
        name="Render HR versions",
        description="Render hight resolution versions",
    )
    render_in_one_line: bpy.props.BoolProperty(
        name="Render all in one line",
        description="Render all in one line of frames",
    )
    hr_scale: bpy.props.FloatProperty(
        name="HR scale",
        description="Scale of hight resolution versions",
        soft_min=1.0,
        soft_max=1.0,
        precision=2,
        default=2.0,
    )

    should_cancel_rendering: bpy.props.BoolProperty(
        name="Should cancel rendering",
        description="Flag to stop rendering spritesheets",
        default=False,
    )

@CLSManager.reg_prop_group(bpy.types.ViewLayer, "factorio")
class FactorioUtils_ViewLayerProps(bpy.types.PropertyGroup):
    output_path: bpy.props.StringProperty(
        name="Output file",
        description="Path to the folder and name of the future spritesheet",
        subtype="FILE_PATH",
    )

@CLSManager.reg_bpy_class
class FACTORIOUTILS_PT_SidePanel(bpy.types.Panel):
    bl_label = "Factorio Utils"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_category = 'Factorio Utils'

    def draw(self, context):
        ob = context.active_object
        active_object = context.scene.factorio.active_object
        scn = bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)

        # secondary label
        def s_label(text):
            nonlocal col
            r = col.row()
            r.alignment = 'RIGHT'
            r.active = False
            r.label(text=text)
            
        s_label(text="Scene Utilities")
        col.operator(operators.FactorioUtils_SetupScene.bl_idname, text="Setup Scene", icon="SCENE_DATA")

        col.separator()
        s_label(text="Options")
        col.prop(scn.factorio, "active_object")
        col.prop(scn.factorio, "render_in_one_line")
        col.prop(scn.factorio, "directions_count")
        col.prop(scn.factorio, "render_hr_versions")
        if scn.factorio.render_hr_versions:
            col.prop(scn.factorio, "hr_scale")

        col.separator()
        s_label(text="Export")
        col.prop(context.view_layer.factorio, "output_path")
        
        bpy.props.StringProperty(name="output", subtype="FILE_PATH")

        progress_bars.render_progress.draw(context, col)
        if not progress_bars.render_progress.progress:
            col.operator(operators.FactorioUtils_RenderAnimations.bl_idname, text=f"Render object animations", icon="OUTPUT")
        else:
            col.operator(
                operators.FactorioUtils_CancelRenderingAnimation.bl_idname,
                text="Cancel rendering", icon="CANCEL")

@CLSManager.reg_bpy_class
class FACTORIOUTILS_PT_ActionSidePanel(bpy.types.Panel):
    bl_label = "Factorio Utils"
    bl_space_type = "NLA_EDITOR"
    bl_region_type = 'UI'
    bl_category = 'Factorio Utils'

    def draw(self, context):
        ob = context.active_object
        active_object = context.scene.factorio.active_object
        scn = bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)
        
        progress_bars.render_progress.draw(context, col)
        if not progress_bars.render_progress.progress:
            active_nla_track = operators.FactorioUtils_RenderOneAnimation.get_active_nla_track(context)
            if active_nla_track is not None:
                col.operator(operators.FactorioUtils_RenderOneAnimation.bl_idname, text=f"Render \"{active_nla_track.name}\" animation", icon="OUTPUT")
        else:
            col.operator(
                operators.FactorioUtils_CancelRenderingAnimation.bl_idname,
                text="Cancel rendering", icon="CANCEL")