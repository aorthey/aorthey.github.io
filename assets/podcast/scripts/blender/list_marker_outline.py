bl_info = {
    "name" : "list-marker-outline",
    "author" : "Andreas Orthey",
    "description" : "Iterate over all markers and write an outline to a txt file.",
    "blender" : (4, 0, 0),
    "version" : (1, 0, 0),
    "location": "Sequencer > Marker Menu",
    "category" : "Sequencer"
}

import bpy
import numpy as np
import pathlib

class ListMarkerOutline(bpy.types.Operator):
    """Create an outline from all markers in the sequence editor."""
    bl_idname = "sequencer.list_marker_outline"
    bl_label = "List Marker Outline"
    bl_options = {'REGISTER'}

    def RaiseError(self, message):
      print("There are time markers out of bounds. Please move them before continuing.")
      self.report({"WARNING"}, message);
      return {'CANCELLED'}

    def execute(self, context):
      scene = context.scene
      fps = scene.render.fps / scene.render.fps_base

      markers = scene.timeline_markers
      markers = sorted(markers, key=lambda item: item.frame)

      outline_string = "Outline\n"
      for marker in markers:
        frame = marker.frame
        if frame > bpy.context.scene.frame_end or frame < bpy.context.scene.frame_start:
          return self.RaiseError("Marker {} is out of bounds at frame \
                                 {}. Please move them before \
                                 continuing.".format(marker.name, marker.frame))

        total_seconds=marker.frame/fps

        minutes=int(np.floor(total_seconds/60.0))
        if minutes < 60:
          seconds=int(total_seconds-60*minutes)
          outline_string+="{:02d}:{:02d} {}\n".format(minutes, seconds, marker.name)
          continue
        hours=int(np.floor(minutes/60.0))
        minutes=int(minutes-hours*60)
        seconds=int(total_seconds-60*minutes-60*60*hours)
        outline_string+="{:02d}:{:02d}:{:02d} {}\n".format(hours, minutes, seconds, marker.name)

      blender_file_path = pathlib.Path(bpy.data.filepath)
      if bpy.data.filepath == '':
        return self.RaiseError("You are working from an unsaved Blend file. Please save the file first.")

      filename = str(blender_file_path.parent / blender_file_path.stem) + ".txt"
      with open(filename, "w") as text_file:
        text_file.write(outline_string)
      self.report({'INFO'}, "Wrote outline to file {}".format(filename))
      return {'FINISHED'}

def menu_function(self, context):
  self.layout.separator()
  self.layout.operator("sequencer.list_marker_outline")

def register():
  bpy.utils.register_class(ListMarkerOutline)
  bpy.types.SEQUENCER_MT_marker.append(menu_function)

def unregister():
  bpy.utils.unregister_class(ListMarkerOutline)
  bpy.types.SEQUENCER_MT_marker.remove(menu_function)

if __name__ == "__main__":
    register()
