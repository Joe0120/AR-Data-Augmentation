import bpy
import math

class Camera:
    def __init__(self, config_setting):
        self.config_setting = config_setting

    def set_camera(self):
        if self.config_setting["blender_env"]["cam_location"]:
            bpy.data.objects['Camera'].location[0] = self.config_setting["blender_env"]["cam_location"][0]
            bpy.data.objects['Camera'].location[1] = self.config_setting["blender_env"]["cam_location"][1]
            bpy.data.objects['Camera'].location[2] = self.config_setting["blender_env"]["cam_location"][2]
        if self.config_setting["blender_env"]["cam_rotation"]:
            bpy.data.objects['Camera'].rotation_euler[0] = math.radians(self.config_setting["blender_env"]["cam_rotation"][0])
            bpy.data.objects['Camera'].rotation_euler[1] = math.radians(self.config_setting["blender_env"]["cam_rotation"][1])
            bpy.data.objects['Camera'].rotation_euler[2] = math.radians(self.config_setting["blender_env"]["cam_rotation"][2])

        bpy.data.objects['Camera'].data.clip_end = self.config_setting["blender_env"]["cam_distance"]
        if self.config_setting["mode_config"]["is_fisheye"]:
            bpy.data.objects['Camera'].data.type = 'PANO'
            bpy.data.objects['Camera'].data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
