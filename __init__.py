bl_info = {
    "name": "Wabi-Sabi Vase Generator",
    "author": "OpenAI",
    "version": (1, 0),
    "blender": (3, 6, 1),
    "location": "View3D > Add > Mesh > Add Vase",
    "description": "Adds a new Wabi-Sabi Vase Mesh Object",
    "category": "Add Mesh",
}

import bpy
from . import properties
from . import operators
from . import panels

def register():
    bpy.utils.register_class(properties.VaseProperties)
    bpy.types.Scene.vase_properties = bpy.props.PointerProperty(type=properties.VaseProperties)
    bpy.utils.register_class(operators.MESH_OT_add_vase)
    bpy.utils.register_class(panels.VASE_PT_vase_panel)

def unregister():
    bpy.utils.unregister_class(properties.VaseProperties)
    del bpy.types.Scene.vase_properties
    bpy.utils.unregister_class(operators.MESH_OT_add_vase)
    bpy.utils.unregister_class(panels.VASE_PT_vase_panel)

if __name__ == "__main__":
    register()
