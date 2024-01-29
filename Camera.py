import bpy
import math

class Camera:
    def __init__(self, config_setting):
        self.config_setting = config_setting
        self.location = {"x":None, "y":None, "z":None}
        self.rotation = {"x":None, "y":None, "z":None}

    def set_camera(self):
        if self.config_setting["blender_env"]["cam_location"]:
            for _idx, key in enumerate(self.location):
                self.location[key] = self.config_setting["blender_env"]["cam_location"][_idx]
                bpy.data.objects['Camera'].location[_idx] = self.config_setting["blender_env"]["cam_location"][_idx]
        else:
            for _idx, key in enumerate(self.location):
                self.location[key] = bpy.data.objects['Camera'].location[_idx]

        if self.config_setting["blender_env"]["cam_rotation"]:
            for _idx, key in enumerate(self.rotation):
                self.rotation[key] = self.config_setting["blender_env"]["cam_rotation"][_idx]
                bpy.data.objects['Camera'].rotation_euler[_idx] = math.radians(self.config_setting["blender_env"]["cam_rotation"][_idx])
        else:
            for _idx, key in enumerate(self.rotation):
                self.rotation[key] = math.degrees(bpy.data.objects['Camera'].rotation_euler[_idx])

        bpy.data.objects['Camera'].data.clip_end = self.config_setting["blender_env"]["cam_distance"]
        if self.config_setting["mode_config"]["is_fisheye"]:
            bpy.data.objects['Camera'].data.type = 'PANO'
            bpy.data.objects['Camera'].data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
