import bpy
import bmesh
import numpy as np
from mathutils import noise
from mathutils import Vector

class MESH_OT_add_vase(bpy.types.Operator):
    bl_idname = "mesh.add_vase"
    bl_label = "Add Vase"
    bl_options = {'REGISTER', 'UNDO'}

    update: bpy.props.BoolProperty(
        name="Update",
        description="If true, update the existing vase. Otherwise, create a new one.",
        default=False,
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
        props = context.scene.vase_properties

        # Define the vase profiles
        vase_profiles = {
            "TYPE_1": [(z, 0.2 + 0.05 * noise.noise_vector(Vector((z, z, z))).length) for z in np.linspace(0, 2, 10)],  # noise
            "TYPE_2": [(z, 0.2 + 0.05 * noise.noise_vector(Vector((z + 10, z + 10, z + 10))).length) for z in np.linspace(0, 2, 10)],  # Different noise
            "TYPE_3": [(z, 0.2 + 0.05 * noise.noise_vector(Vector((z + 20, z + 20, z + 20))).length) for z in np.linspace(0, 2, 10)],  # Yet another noise
        }

        # Get the vase profile
        profile = vase_profiles[props.vase_type]

        # Normalize the vase height
        profile = [(z / profile[-1][0] * props.height, r) for z, r in profile]

        # Pad the profile with repeated end points for the Catmull-Rom spline
        profile = [profile[0]] + profile + [profile[-1]]

        # Interpolate the vase profile
        z = np.linspace(0, props.height, props.segments)
        r = np.empty_like(z)
        for i in range(len(profile) - 3):
            z_segment, r_segment = self.catmull_rom(profile[i], profile[i+1], profile[i+2], profile[i+3])
            mask = (z >= z_segment[0]) & (z <= z_segment[-1])
            r[mask] = np.interp(z[mask], z_segment, r_segment)

        # Define the parameters for the vase
        theta = np.linspace(0, 2 * np.pi, props.segments)  # theta parameter
        z, theta = np.meshgrid(z, theta)

        # Add spiral pattern and asymmetry
        spiral = z / 10  # controls the tightness of the spiral
        z_flat = np.ravel(z)
        theta_flat = np.ravel(theta)

        asymmetry = np.array([0.05 * noise.noise(Vector((z_ij, theta_ij, z_ij))) for z_ij, theta_ij in zip(z_flat, theta_flat)])  # controls the degree of asymmetry
        relief = np.array([0.05 * noise.noise(Vector((z_ij + theta_ij, z_ij + theta_ij, z_ij + theta_ij))) for z_ij, theta_ij in zip(z_flat, theta_flat)])  # controls the degree of relief

        asymmetry = np.reshape(asymmetry, z.shape)
        relief = np.reshape(relief, z.shape)

        r += spiral + asymmetry + relief

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
