import bpy
import bmesh
import numpy as np
from scipy.interpolate import CubicSpline

class VaseProperties(bpy.types.PropertyGroup):
    vase_types = [
        ("TYPE_1", "Type 1", "Wabi-Sabi Vase 1"),
        ("TYPE_2", "Type 2", "Wabi-Sabi Vase 2"),
        ("TYPE_3", "Type 3", "Wabi-Sabi Vase 3"),
    ]

    vase_type: bpy.props.EnumProperty(name="Vase Type", items=vase_types, default="TYPE_1")
    segments: bpy.props.IntProperty(name="Segments", default=100, min=3, max=1000)
    height: bpy.props.FloatProperty(name="Height", default=2.0, min=0.1, max=10.0)

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

        # Define the vase profiles
        vase_profiles = {
            "TYPE_1": [(0.0, 0.2), (0.5, 1.0), (1.0, 0.8), (1.5, 0.6), (2.0, 0.4)],
            "TYPE_2": [(0.0, 0.8), (1.0, 0.7), (2.0, 0.6)],
            "TYPE_3": [(0.0, 0.2), (1.0, 1.0), (2.0, 0.2)],
        }

        # Get the vase profile
        profile = vase_profiles[props.vase_type]

        # Normalize the vase height
        profile = [(z / profile[-1][0] * props.height, r) for z, r in profile]

        # Interpolate the vase profile
        z_points, r_points = zip(*profile)
        spline = CubicSpline(z_points, r_points)
        z = np.linspace(0, props.height, props.segments)
        r = spline(z)

        # Define the parameters for the vase
        theta = np.linspace(0, 2 * np.pi, props.segments)  # theta parameter
        z, theta = np.meshgrid(z, theta)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

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
