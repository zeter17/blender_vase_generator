import bpy

class VaseProperties(bpy.types.PropertyGroup):
    vase_types = [
        ("TYPE_1", "Type 1", "Wabi-Sabi Vase 1"),
        ("TYPE_2", "Type 2", "Wabi-Sabi Vase 2"),
        ("TYPE_3", "Type 3", "Wabi-Sabi Vase 3"),
    ]

    vase_type: bpy.props.EnumProperty(name="Vase Type", items=vase_types, default="TYPE_1")
    segments: bpy.props.IntProperty(name="Segments", default=100, min=3, max=1000)
    height: bpy.props.FloatProperty(name="Height", default=2.0, min=0.1, max=10.0)
