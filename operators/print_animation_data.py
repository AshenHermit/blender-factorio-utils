from email.policy import default
from inspect import trace
import math
import traceback
import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
from .render_animations import FactorioUtils_RenderOneAnimation
from ..classes_manager import CLSManager

from ..info import addon_id, rotator_name
from ..menu_operator import MenuOperator

@CLSManager.reg_bpy_class
class FactorioUtils_PrintAnimationData(MenuOperator):
    bl_idname = f"factorio.print_animation_data"
    bl_label = "Factorio Utils: Print lua animation data"
    bl_category = "Object"
    bl_options = {"REGISTER",}
    menu_type = bpy.types.TEXT_MT_text
    
    @classmethod
    def draw_menu(cls, self, context):
        if context.scene.factorio.active_object:
            for nla_track in context.scene.factorio.active_object.animation_data.nla_tracks.values():
                op = self.layout.operator(cls.bl_idname, text=f"Print lua animation for \"{nla_track.name}\"")
                op.nla_track_name = nla_track.name
                
    nla_track_name: bpy.props.StringProperty(
        name="Animation name",
        default="",
    )

    def __init__(self) -> None:
        self.text = ""
        self.indent = 0
    
    def wl(self, text):
        indent = "  " * self.indent
        self.text += indent + text + "\n"

    def render_animation_data(self, context):
        self.indent = 0
        self.text = ""

        if context.scene.factorio.active_object is None: raise Exception("no active object specified")
        if self.nla_track_name != "":
            nla_track = context.scene.factorio.active_object.animation_data.nla_tracks.get(self.nla_track_name)
        if nla_track is None: raise Exception("nla track not found")

        def get_sprite_path(hr=False):
            path = FactorioUtils_RenderOneAnimation.get_spritesheet_filepath(context, nla_track, hr)
            lua_path = f'"{path.as_posix()}"'
            try:
                rel_path = "/".join(path.parts[list(path.parts).index("graphics")+1:])
                lua_path = f'graphics_path .. "{rel_path}"'
            except:
                try:
                    rel_path = "/".join(path.parts[list(path.parts).index("mods")+2:])
                    lua_path = f'mod_path .. "{rel_path}"'
                except:
                    traceback.print_exc()
                traceback.print_exc()
            return lua_path
        
        hr_scale = context.scene.factorio.hr_scale
        frame_size = (context.scene.render.resolution_x,
                        context.scene.render.resolution_y)
        hr_frame_size = (frame_size[0]*hr_scale, frame_size[1]*hr_scale)

        start_frame = min([s.frame_start for s in nla_track.strips])
        end_frame = max([s.frame_end for s in nla_track.strips])
        frames_count = int(end_frame-start_frame)
        total_frames_count = frames_count * context.scene.factorio.directions_count

        line_length = math.ceil(math.sqrt(total_frames_count))
        if context.scene.factorio.render_in_one_line:
            line_length = total_frames_count
        
        animation_speed = bpy.context.scene.render.fps/60.0
        direction_count = context.scene.factorio.directions_count

        in_game_scale = 32.0 / (max(frame_size[0], frame_size[1]) / bpy.context.scene.camera.data.ortho_scale)

        self.wl('--#-- for animation / rotated animation - https://lua-api.factorio.com/1.1.107/types/RotatedAnimation.html')
        self.wl('{')
        self.indent+=1
        self.wl(f'filename = {get_sprite_path()},')
        self.wl('priority = "high",')
        self.wl(f'width = {frame_size[0]},')
        self.wl(f'height = {frame_size[1]},')
        self.wl('shift = { 0, 0 },')
        self.wl(f'frame_count = {frames_count},')
        self.wl(f'line_length = {line_length},')
        if(direction_count>1): self.wl(f'direction_count = {direction_count},')
        self.wl(f'animation_speed = {animation_speed},')
        self.wl(f'scale = {in_game_scale},')

        if context.scene.factorio.render_hr_versions:
            self.wl('hr_version = {')
            self.indent+=1
            self.wl(f'filename = {get_sprite_path(True)},')
            self.wl('priority = "high",')
            self.wl(f'width = {frame_size[0]} * {hr_scale},')
            self.wl(f'height = {frame_size[1]} * {hr_scale},')
            self.wl('shift = { 0, 0 },')
            self.wl(f'frame_count = {frames_count},')
            self.wl(f'line_length = {line_length},')
            if(direction_count>1): self.wl(f'direction_count = {direction_count},')
            self.wl(f'animation_speed = {animation_speed},')
            self.wl(f'scale = {in_game_scale} / {hr_scale},')
            self.indent-=1
            self.wl('},')
    
        self.indent-=1
        self.wl('},')
        self.wl('')

        if(direction_count>1):
            self.wl('--#-- for SpriteNWaySheet - needs "Render in one line" turned on - https://lua-api.factorio.com/1.1.107/types/SpriteNWaySheet.html')
            self.wl('sheet = {')
            self.indent+=1
            self.wl(f'filename = {get_sprite_path()},')
            self.wl(f'frames = {direction_count},')
            self.wl(f'width = {frame_size[0]},')
            self.wl(f'height = {frame_size[1]},')
            self.wl(f'scale = {in_game_scale},')
            self.wl('shift = { 0, 0 },')
            self.indent-=1
        self.wl('},')

        self.text = self.text.strip()
        
        return self.text

    def execute(self, context):
        try:
            text = self.render_animation_data(context)
        except Exception as e:
            traceback.print_exc()
            text = e.args[0] if len(e.args)>0 else ""
        
        text_data_name = "animation_data_lua"
        text_data = bpy.data.texts.get(text_data_name)
        if text_data is None:
            bpy.ops.text.new()
            text_data = bpy.data.texts[-1]
            text_data.name = text_data_name
        context.space_data.text = text_data

        text_data.clear()
        text_data.write(text)

        return {"FINISHED"}
