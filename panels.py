import bpy

class VASE_PT_vase_panel(bpy.types.Panel):
    bl_label = "Wabi-Sabi Vase Generator"
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

        # Draw the "Add Vase" and "Update Vase" buttons
        row = layout.row()
        row.operator("mesh.add_vase", text="Add Vase")
        row.operator("mesh.add_vase", text="Update Vase").update = True
