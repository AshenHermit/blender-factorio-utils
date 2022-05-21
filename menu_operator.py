from functools import partial
import bpy
import bpy.types

class MenuOperator(bpy.types.Operator):
    bl_options = {"REGISTER",}
    menu_type = bpy.types.VIEW3D_MT_object
    menu_group = ""
    _first_used_types = {}

    @classmethod
    def get_used_type_key(cls):
        return str(cls.menu_type)+cls.menu_group

    @classmethod
    def find_used_type(cls):
        return MenuOperator._first_used_types.get(cls.get_used_type_key(), None)

    @classmethod
    def draw_menu(cls, self, context):
        self.layout.operator(cls.bl_idname, text=cls.bl_label)

    @classmethod
    def register_to_menu(cls):
        def draw_func(self, context):
            nonlocal cls
            if cls.find_used_type() is cls:
                self.layout.separator()
            cls.draw_menu(self, context)
        
        if cls.find_used_type() is None:
            MenuOperator._first_used_types[cls.get_used_type_key()] = cls

        cls.menu_type.append(draw_func)