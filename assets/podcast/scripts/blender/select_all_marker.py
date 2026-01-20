bl_info = {
    "name": "Select All Markers in Sequencer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Video Sequence Editor > Marker > Select All",
    "description": "Adds a 'Select All' entry to the Marker menu in the Video Sequence Editor to select all timeline markers.",
    "category": "Sequencer",
}

import bpy

class SEQUENCER_OT_select_all_markers(bpy.types.Operator):
    """Select all timeline markers"""
    bl_idname = "sequencer.select_all_markers"
    bl_label = "Select All"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        # Use the built-in marker select_all operator with SELECT action
        bpy.ops.marker.select_all(action='SELECT')
        return {'FINISHED'}

def menu_draw(self, context):
    self.layout.operator(SEQUENCER_OT_select_all_markers.bl_idname)

def register():
    bpy.utils.register_class(SEQUENCER_OT_select_all_markers)
    bpy.types.SEQUENCER_MT_marker.append(menu_draw)

def unregister():
    bpy.types.SEQUENCER_MT_marker.remove(menu_draw)
    bpy.utils.unregister_class(SEQUENCER_OT_select_all_markers)

if __name__ == "__main__":
    register()

