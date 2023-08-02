bl_info = {
    "name": "Vase Generator",
    "author": "OpenAI",
    "version": (1, 0),
    "blender": (3, 6, 1),
    "location": "View3D > Add > Mesh > Add Vase",
    "description": "Adds a new Vase Mesh Object",
    "category": "Add Mesh",
}

import bpy
import bmesh
import numpy as np

class VaseProperties(bpy.types.PropertyGroup):
    vase_types = [
        ("TYPE_1", "Type 1", "Standard Vase"),
        ("TYPE_2", "Type 2", "Thinner Vase with Pronounced Waist"),
        ("TYPE_3", "Type 3", "Vase with Bulbous Bottom and Narrow Top"),
    ]

    vase_type: bpy.props.EnumProperty(name="Vase Type", items=vase_types, default="TYPE_1")
    segments: bpy.props.IntProperty(name="Segments", default=100, min=3, max=1000)
    height: bpy.props.FloatProperty(name="Height", default=2.0, min=0.1, max=10.0)
    thinness: bpy.props.FloatProperty(name="Thinness", default=0.5, min=0.1, max=2.0)

class MESH_OT_add_vase(bpy.types.Operator):
    bl_idname = "mesh.add_vase"
    bl_label = "Add Vase"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the vase properties
        props = context.scene.vase_properties

        # Delete the old vase if it exists
        if "vase" in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects["vase"], do_unlink=True)

        # Define the parameters for the vase
        u = np.linspace(0, 2 * np.pi, props.segments)  # u parameter
        v = np.linspace(-props.height, props.height, props.segments)  # v parameter
        u, v = np.meshgrid(u, v)

        # Define the parametric equations for the vase
        if props.vase_type == "TYPE_1":
            r = props.thinness + 0.1 * np.cos(np.pi * v)  # radius
        elif props.vase_type == "TYPE_2":
            r = props.thinness + 0.05 * np.cos(2 * np.pi * v)  # radius
        elif props.vase_type == "TYPE_3":
            r = props.thinness + 0.1 * (1 + np.cos(np.pi * v))  # radius

        x = r * np.cos(u)
        y = r * np.sin(u)
        z = v

        # Create a new mesh and link it to the scene
        mesh = bpy.data.meshes.new("vase")
        obj = bpy.data.objects.new("vase", mesh)
        context.collection.objects.link(obj)

        # Create the vase mesh
        bm = bmesh.new()
        for i in range(x.shape[0] - 1):
            for j in range(x.shape[1] - 1):
                # Create a new face for each square in the grid
                verts = [
                    bm.verts.new((x[i][j], y[i][j], z[i][j])),
                    bm.verts.new((x[i+1][j], y[i+1][j], z[i+1][j])),
                    bm.verts.new((x[i+1][j+1], y[i+1][j+1], z[i+1][j+1])),
                    bm.verts.new((x[i][j+1], y[i][j+1], z[i][j+1])),
                ]
                bm.faces.new(verts)

        # Add the bottom face to close the vase
        bottom_verts = [bm.verts.new((x[i][0], y[i][0], z[i][0])) for i in range(x.shape[0] - 1)]
        bm.faces.new(bottom_verts)

        # Update the mesh with the new data
        bm.to_mesh(mesh)
        bm.free()

        return {'FINISHED'}

class VASE_PT_vase_panel(bpy.types.Panel):
    bl_label = "Vase Generator"
    bl_idname = "VASE_PT_vase_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Vase Generator"

    def draw(self, context):
        layout = self.layout
        props = context.scene.vase_properties

        # Draw the vase properties
        layout.prop(props, "vase_type")
        layout.prop(props, "segments")
        layout.prop(props, "height")
        layout.prop(props, "thinness")

        # Draw the "Add Vase" button
        layout.operator(MESH_OT_add_vase.bl_idname)

def menu_func(self, context):
    self.layout.operator(MESH_OT_add_vase.bl_idname)

def register():
    bpy.utils.register_class(VaseProperties)
    bpy.types.Scene.vase_properties = bpy.props.PointerProperty(type=VaseProperties)
    bpy.utils.register_class(MESH_OT_add_vase)
    bpy.utils.register_class(VASE_PT_vase_panel)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(VaseProperties)
    del bpy.types.Scene.vase_properties
    bpy.utils.unregister_class(MESH_OT_add_vase)
    bpy.utils.unregister_class(VASE_PT_vase_panel)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
