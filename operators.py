import bpy
import bmesh
import numpy as np
from mathutils import Vector
import random

class MESH_OT_add_vase(bpy.types.Operator):
    bl_idname = "mesh.add_vase"
    bl_label = "Add Vase"
    bl_options = {'REGISTER', 'UNDO'}

    vase_type: bpy.props.EnumProperty(
        name="Vase Type",
        description="The type of the vase to create",
        items=[
            ("CLASSIC", "Classic", "Classic vase shape"),
            ("MODERN", "Modern", "Modern vase shape"),
            ("ABSTRACT", "Abstract", "Abstract vase shape"),
        ],
        default="CLASSIC",
    )

    segments: bpy.props.IntProperty(
        name="Segments",
        description="The number of segments to use when creating the vase",
        default=100,
        min=3,
    )

    height: bpy.props.FloatProperty(
        name="Height",
        description="The height of the vase",
        default=1.0,
        min=0.1,
    )

    def catmull_rom(self, P0, P1, P2, P3, n=100):
        """
        Catmull-Rom spline.
        
        P0, P1, P2, and P3 are the control points.
        n is the number of points to include in this curve segment.
        """
        # Parameter values
        t = np.linspace(0, 1, n)
        
        # The basis matrix for a Catmull-Rom spline
        M = np.array([
            [-1, 3, -3, 1],
            [2, -5, 4, -1],
            [-1, 0, 1, 0],
            [0, 2, 0, 0]
        ]) / 2
        
        # The control points
        P = np.array([P0, P1, P2, P3])
        
        # The parameter matrix
        T = np.array([t**3, t**2, t, np.ones_like(t)])
        
        # The curve points
        C = np.dot(M, P).T.dot(T)
        
        return C

    def execute(self, context):
        # Get the vase properties
        vase_type = self.vase_type
        segments = self.segments
        height = self.height

        theta = np.linspace(0, 2. * np.pi, segments)
        z = np.linspace(0, height, segments)
        theta, z = np.meshgrid(theta, z)

        vase_profiles = {
            "CLASSIC": [(z_i, 0.2 + 0.1 * random.random()) for z_i in np.linspace(0, 1, self.segments)],
            "MODERN": [(z_i, 0.2 + 0.05 * np.sin(2 * np.pi * z_i)) for z_i in np.linspace(0, 1, self.segments)],
            "ABSTRACT": [(z_i, 0.2 + 0.1 * random.random()) for z_i in np.linspace(0, 1, self.segments)],
        }
        profile = vase_profiles[vase_type]
        r = np.array(vase_profiles[vase_type])
        # Add random noise to create organic shape
        r += np.random.normal(loc=0.0, scale=0.02, size=r.shape)

        # Normalize the vase height
        profile = [(z / profile[-1][0] * height, r) for z, r in profile]
        # Pad the profile with repeated end points for the Catmull-Rom spline
        profile = [profile[0]] + profile + [profile[-1]]

        # Interpolate the vase profile
        z = np.linspace(0, height, segments)
        r = np.zeros_like(z)
        for i in range(len(profile) - 3):
            z_segment, r_segment = self.catmull_rom(profile[i], profile[i+1], profile[i+2], profile[i+3])
            mask = (z >= z_segment[0]) & (z <= z_segment[-1])
            r[mask] = np.interp(z[mask], z_segment, r_segment)

        # Define the parameters for the vase
        theta = np.linspace(0, 2 * np.pi, segments)  # theta parameter
        z, theta = np.meshgrid(z, theta)
        # Add spiral pattern and asymmetry
        spiral = z / 10  # controls the tightness of the spiral

        asymmetry = np.array([0.05 * random.uniform(-1, 1) for _ in np.ravel(z)])  # controls the degree of asymmetry
        relief = np.array([0.05 * random.uniform(-1, 1) for _ in np.ravel(z)])  # controls the degree of relief

        r = r + spiral + asymmetry.reshape(z.shape) + relief.reshape(z.shape)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Get the current object or create a new one
        if context.object and context.object.name.startswith("vase"):
            obj = context.object
            mesh = obj.data
            mesh.clear_geometry()
        else:
            mesh = bpy.data.meshes.new("vase")
            obj = bpy.data.objects.new("vase", mesh)
            context.collection.objects.link(obj)
            context.view_layer.objects.active = obj

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
