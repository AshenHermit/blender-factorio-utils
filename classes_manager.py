from ast import operator
import bpy

class CLSManager:
    class AddDrawFunc():
        def __init__(self, bpy_type, func, prepend=False) -> None:
            self.bpy_type = bpy_type
            self.func = func
            self.prepend = False

    class NewPropGroup():
        def __init__(self, in_type, group_name, group_cls) -> None:
            self.in_type = in_type
            self.group_name = group_name
            self.group_cls = group_cls
    
    bpy_classes = []
    prop_groups:list[NewPropGroup] = []
    add_draw_funcs:list[AddDrawFunc] = []

    @classmethod
    def reg_bpy_class(self_cls, cls_to_reg):
        self_cls.bpy_classes.append(cls_to_reg)
        return cls_to_reg

    @classmethod
    def reg_prop_group(self_cls, in_type=None, group_name=""):
        def wrapper(cls_to_reg):
            nonlocal in_type, group_name
            self_cls.bpy_classes.append(cls_to_reg)
            self_cls.prop_groups.append(
                self_cls.NewPropGroup(in_type, group_name, cls_to_reg))
            return cls_to_reg
        return wrapper

    @classmethod
    def reg_draw_func(self_cls, bpy_type, prepend=False):
        def decorator(func):
            nonlocal bpy_type, prepend
            self_cls.add_draw_funcs.append(self_cls.AddDrawFunc(bpy_type, func, prepend))
            return func
        return decorator

    @classmethod
    def register(self_cls):
        for cls in self_cls.bpy_classes:
            bpy.utils.register_class(cls)
            
            if hasattr(cls, "register_to_menu"):
                getattr(cls, "register_to_menu")()

        for newgroup in self_cls.prop_groups:
            prop = bpy.props.PointerProperty(name="prop_group", type = newgroup.group_cls)
            setattr(newgroup.in_type, newgroup.group_name, prop)

        for draw_func in self_cls.add_draw_funcs:
            if draw_func.prepend: draw_func.bpy_type.prepend(draw_func.func)
            else: draw_func.bpy_type.append(draw_func.func)

    @classmethod
    def unregister(self_cls):
        for cls in self_cls.bpy_classes:
            bpy.utils.unregister_class(cls)
    