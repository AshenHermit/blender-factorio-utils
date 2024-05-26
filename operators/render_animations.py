import time
import traceback
import bpy
import bmesh
import addon_utils
import bpy.types
from bpy_extras.io_utils import ImportHelper
from pathlib import Path
import shutil
import math

from PIL import Image
import PIL
from ..classes_manager import CLSManager

from ..menu_operator import MenuOperator

from ..info import addon_id, rotator_name
from .. import progress_bars
from ..props_getters import props_manager

@CLSManager.reg_bpy_class
class FactorioUtils_CancelRenderingAnimation(bpy.types.Operator):
    bl_idname = f"factorio.cancel_rendering_animation"
    bl_label = "Factorio Utils: Cancel rendering animations"
    
    def execute(self, context):
        context.scene.factorio.should_cancel_rendering = True
        return {"FINISHED"}

@CLSManager.reg_bpy_class
class FactorioUtils_RenderAnimations(MenuOperator):
    bl_idname = f"factorio.render_animations"
    bl_label = "Factorio Utils: Render all animations of active object"
    bl_category = "Render"
    bl_options = {"REGISTER",}
    menu_type = bpy.types.TOPBAR_MT_render

    def __init__(self) -> None:
        self.timer = None
        self.current_nla_track_idx = 0

    def modal(self, context, event):
        if event.type != "TIMER": return {'PASS_THROUGH'}

        if context.scene.factorio.should_cancel_rendering:
            context.window_manager.event_timer_remove(self.timer)
            return {"FINISHED"}

        obj = context.scene.factorio.active_object
        scene = context.scene

        nla_tracks = obj.animation_data.nla_tracks.values()

        if self.current_nla_track_idx < len(nla_tracks):
            if progress_bars.render_progress.progress==0.0:
                obj.animation_data.nla_tracks.active = nla_tracks[self.current_nla_track_idx]
                bpy.ops.factorio.render_one_animation('INVOKE_DEFAULT')
                self.current_nla_track_idx+=1
            return {'PASS_THROUGH'}
        else:
            context.window_manager.event_timer_remove(self.timer)
            return {"FINISHED"}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        context.scene.factorio.should_cancel_rendering = False
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.05, window=context.window)
        
        return {'RUNNING_MODAL'}

@CLSManager.reg_bpy_class
class FactorioUtils_RenderOneAnimation(MenuOperator):
    class AnimationStruct:
        def __init__(self, name=None, loop=True, speed=18, frames=None) -> None:
            self.name = name or "animation"
            self.loop = loop
            self.speed = speed
            self.frames = frames or []

    bl_idname = f"factorio.render_one_animation"
    bl_label = "Factorio Utils: Render active animation of active object"
    bl_category = "Render"
    menu_type = bpy.types.TOPBAR_MT_render
    
    def __init__(self):
        self.rotator = None
        self.rotator_start_z_angle = 0.0

        self.timer = None
        self.wait_state = 0
        self.done = False
        self.render_progress = 0

        self.animation = None
        self.nla_track = None

        self.directions_count = 1
        self.start_frame = 0
        self.end_frame = 1
        self.current_direction = 0
        self.current_frame = 0

        self.spritesheet_filepath:Path = None
        self.tmp_dir = None
        self.frame_wait = None
    
    @staticmethod
    def get_active_nla_track(context):
        try:
            nla_track = context.scene.factorio.active_object.animation_data.nla_tracks.active
            return nla_track
        except:
            try:
                nla_track = context.scene.factorio.active_object.animation_data.nla_tracks.values()[0]
                return nla_track
            except:
                return None

    @staticmethod
    def get_spritesheet_filepath(context, nla_track, hr=False):
        if nla_track is None: return None

        output_file_prop = props_manager.spritesheet_output_path
        output_filename = output_file_prop.with_suffix("").name
        name = f"{output_filename}-{nla_track.name}.png"
        if hr: name = "hr-" + name
        spritesheet_filepath = output_file_prop.with_name(name)
        return spritesheet_filepath

    def update_rotator(self, context):
        self.rotator.rotation_euler[2] = (math.pi*2/self.directions_count)*self.current_direction

    def render_frame(self, context):
        # self.nla_track.is_solo = True
        self.update_rotator(context)

        self.current_frame = int(self.current_frame)
        context.scene.frame_current = self.current_frame
        filename = f"{self.current_direction}-{self.current_frame}"
        output_file = (self.tmp_dir/filename).with_suffix(".png")
        context.scene.render.filepath = output_file.with_suffix("").as_posix()
        bpy.ops.render.render(animation=False, write_still=True)

        frame = Image.open(output_file)
        self.animation.frames.append(frame)

        # self.nla_track.is_solo = False
    def compose_spritesheet(self, x_capacity, y_capacity, frames):
        image_size = frames[0].size
        sheet_image = Image.new('RGBA', (x_capacity*image_size[0], y_capacity*image_size[1]), (0, 0, 0, 0))

        for i, frame in enumerate(frames):
            x = image_size[0] * (i % x_capacity)
            y = image_size[1] * (i // x_capacity)
            sheet_image.paste(frame, (x, y))

        return sheet_image
    
    def make_spritesheet_line(self, animation:AnimationStruct):
        if len(animation.frames)==0: return None

        sheet_x_cap = len(animation.frames)
        sheet_y_cap = 1

        return self.compose_spritesheet(sheet_x_cap, sheet_y_cap, animation.frames)
    
    def make_spritesheet(self, animation:AnimationStruct):
        if len(animation.frames)==0: return None

        sheet_x_cap = math.ceil(math.sqrt(len(animation.frames)))
        sheet_y_cap = math.ceil(len(animation.frames)/sheet_x_cap)

        return self.compose_spritesheet(sheet_x_cap, sheet_y_cap, animation.frames)

    def save_spritesheet(self, context):
        spritesheet = None
        if context.scene.factorio.render_in_one_line:
            spritesheet = self.make_spritesheet_line(self.animation)
        else:
            spritesheet = self.make_spritesheet(self.animation)
        
        if spritesheet is not None:
            progress_bars.render_progress.update(99, "Saving")

            filepath = self.spritesheet_filepath
            if context.scene.factorio.render_hr_versions:
                filepath = filepath.with_name("hr-"+filepath.name)
                spritesheet.save(filepath)
                size = tuple(map(lambda x: int(x//context.scene.factorio.hr_scale), list(spritesheet.size)))
                spritesheet = spritesheet.resize(size, Image.BICUBIC)
                filepath = self.spritesheet_filepath
            spritesheet.save(filepath)

    def modal(self, context, event):
        if event.type != "TIMER": return {'PASS_THROUGH'}

        if context.scene.factorio.should_cancel_rendering:
            progress_bars.render_progress.update(100, "Canceled")
            self.end_rendering(context)
            return {'FINISHED'}

        if self.wait_state<1:
            self.wait_state+=1
            return {'PASS_THROUGH'}
        else:
            self.wait_state = 0
        
        if self.current_direction < self.directions_count:
            if self.current_frame < self.end_frame:
                progress_bars.render_progress.update(1+
                    self.render_progress * 98/(self.directions_count*(self.end_frame-self.start_frame)), 
                    f"Rendering \"{self.nla_track.name}-{self.current_direction}-{self.current_frame}\"")
                
                self.render_frame(context)

                self.current_frame += 1
                self.render_progress += 1
                return {'PASS_THROUGH'}

            else:
                self.current_frame = self.start_frame
                self.current_direction += 1

                if self.current_direction==self.directions_count:
                    progress_bars.render_progress.update(99, "Saving")
                
            return {'PASS_THROUGH'}

        elif not self.done:
            progress_bars.render_progress.update(
                99/(self.directions_count*(self.end_frame-self.start_frame)), 
                f"Saving spritesheet \"{self.current_direction}-{self.current_frame}\"")
            self.save_spritesheet(context)
            self.done = True
            return {'PASS_THROUGH'}

        else:
            progress_bars.render_progress.update(100, "Done")
            self.end_rendering(context)
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def start_rendering(self, context):
        if context.scene.factorio.render_hr_versions:
            context.scene.render.resolution_percentage = int(100 * context.scene.factorio.hr_scale)

        self.nla_track.is_solo = True

        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def end_rendering(self, context):
        context.window_manager.event_timer_remove(self.timer)
        context.scene.render.resolution_percentage = 100
        self.current_direction = 0
        self.current_frame = self.start_frame
        context.scene.frame_current = int(self.current_frame)
        self.rotator.rotation_euler[2] = self.rotator_start_z_angle

        for frame in self.animation.frames:
            try:
                frame.close()
            except:
                traceback.print_exc()

        self.nla_track.is_solo = False
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        
    def invoke(self, context, event):
        context.scene.factorio.should_cancel_rendering = False

        self.wait_state = 0
        self.rotator = context.view_layer.objects.get(rotator_name)
        self.rotator_start_z_angle = self.rotator.rotation_euler[2]

        self.nla_track = self.get_active_nla_track(context)
        if self.nla_track is None:
            return {"CANCELED"}
        self.nla_track.is_solo = True
        self.directions_count = context.scene.factorio.directions_count

        self.animation = self.AnimationStruct(self.nla_track.name, True, context.scene.render.fps, [])

        self.start_frame = min([s.frame_start for s in self.nla_track.strips])
        self.end_frame = max([s.frame_end for s in self.nla_track.strips])

        self.current_direction = 0
        self.current_frame = int(self.start_frame)
        
        self.done = False
        
        output_file_prop = props_manager.spritesheet_output_path
        self.tmp_dir = output_file_prop.parent/"__tmp__render__"
        output_filename = output_file_prop.with_suffix("").name
        self.spritesheet_filepath = output_file_prop.with_name(f"{output_filename}-{self.animation.name}.png")

        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.05, window=context.window)

        self.start_rendering(context)

        progress_bars.render_progress.update(1, "Starting to render")
        
        return {'RUNNING_MODAL'}