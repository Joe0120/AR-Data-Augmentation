import cv2,os,bpy
import bpy_extras
import mathutils
import numpy as np
import itertools
from mathutils import Vector
import math

class BBOX:
    def __init__(self, config_setting):
        self.config_setting = config_setting
    
    def get_bbox_2D(self, filename):
        segmentation_mask = cv2.imread(filename+'.png', cv2.IMREAD_UNCHANGED)
        non_zero_pixels = np.argwhere(segmentation_mask[:, :, 3] > 0)
        if not non_zero_pixels.any(): return None
        
        left_top = non_zero_pixels.min(axis=0)
        right_bottom = non_zero_pixels.max(axis=0)
        width = right_bottom[0] - left_top[0]
        height = right_bottom[1] - left_top[1]
        if (width < self.config_setting["mode_config"]["smallest_obj_size"][0]) or (height < self.config_setting["mode_config"]["smallest_obj_size"][1]): 
            return None
        return [tuple(left_top[::-1]), tuple(right_bottom[::-1])]
    
    def get_bbox_3D(self):
        def np_matmul_coords(coords, matrix, space=None):
            M = (space @ matrix @ space.inverted()
                if space else matrix).transposed()
            ones = np.ones((coords.shape[0], 1))
            coords4d = np.hstack((coords, ones))
            return np.dot(coords4d, M)[:,:-1]
        coords = np.vstack(
            tuple(np_matmul_coords(np.array(o.bound_box), o.matrix_world.copy())
                for o in bpy.context.scene.objects 
                    if o.type == 'MESH' 
                )
            )
        bfl = coords.min(axis=0)
        # top back right
        tbr = coords.max(axis=0)
        G  = np.array((bfl, tbr)).T
        # bound box coords ie the 8 combinations of bfl tbr.
        bbc = [i for i in itertools.product(*G)]

        return np.array(bbc)

    def get_bbox3D_loc(self, bbc):
        data = np.array(bbc)
        print(np.round(data, 2))
        center = np.mean(data, axis=0)
        obj_height = np.max(data[:, 2])-np.min(data[:, 2])
        center[2] = (obj_height/1.65) - (obj_height-2)/2
        closest_top_rounded = np.round(center, 2)
        print(closest_top_rounded)
        return [-closest_top_rounded[1], closest_top_rounded[2], closest_top_rounded[0]]
    
    def get_bev_alpha(self, material_args):
        return math.atan2(material_args["location_x"], material_args["location_y"])

    def get_bev_rotation_y(self, material_args):
        z = [0, 45, 90, 135, 180, 225, 270, 315]
        bev_rotation_y = [0, -0.785, -1.57, -2.355, 3.14, 2.355, 1.57, 0.785]
        return bev_rotation_y[z.index(material_args["rotation_z"])]
        return -(math.atan2(material_args["location_x"], material_args["location_y"]) + math.radians(material_args["rotation_z"]-101))
        
