import bpy
import math

class Camera:
    def __init__(self, config_setting):
        self.config_setting = config_setting

    def set_camera(self):
        # bpy.data.objects['Camera'].location[0] = 0
        # bpy.data.objects['Camera'].location[1] = 0
        # bpy.data.objects['Camera'].location[2] = 3
        # bpy.data.objects['Camera'].rotation_euler[0] = math.radians(82)
        # bpy.data.objects['Camera'].rotation_euler[1] = 0
        # bpy.data.objects['Camera'].rotation_euler[2] = 0
        bpy.data.objects['Camera'].data.clip_end = self.config_setting["blender_env"]["cam_distance"]
        if self.config_setting["mode_config"]["is_fisheye"]:
            bpy.data.objects['Camera'].data.type = 'PANO'
            bpy.data.objects['Camera'].data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
