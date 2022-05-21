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

from .info import addon_id

class ProgressAgent():
    def __init__(self, id:str) -> None:
        self._id = id
        self.context = None
        self.label = ""
        self._progress = 0.0

    @property
    def prop_id(self):
        return "factorio_utils_" + self._id
    
    @property
    def progress(self):
        return self._progress
        if self.context is None: return 0.0
        return getattr(self.context.scene, self.prop_id)

    @progress.setter
    def progress(self, value):
        self._progress = value
        return setattr(self.context.scene, self.prop_id, value)

    def draw(self, context, layout):
        self.context = context
        if self.progress:
            progress_bar = layout.row()
            progress_bar.prop(self.context.scene, self.prop_id)
            progress_lbl = layout.row()
            progress_lbl.active = False
            progress_lbl.label(text=self.label)
        else:
            pass

    def update(self, value, label=""):
        if value == 100.0: value = 0.0
        self.progress = value
        self.label = label
        if self.context is not None: self.context.area.tag_redraw()
        
    def register(self):
        setattr(bpy.types.Scene, self.prop_id, 
            bpy.props.FloatProperty(
                name=self._id.replace("_", " ").title(),
                subtype="PERCENTAGE",
                soft_min=0, 
                soft_max=100, 
                precision=0,
            )
        )
        pass

render_progress = ProgressAgent("render_progress")

progress_agents = [render_progress]