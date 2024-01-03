import cv2,os,bpy
import bpy_extras
import mathutils
import numpy as np
import itertools
from mathutils import Vector

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
    
    def get_segmentation(self, filename):
        image = cv2.imread(filename+'.png', cv2.IMREAD_UNCHANGED)
        height, width = image.shape[:2]
        alpha_channel = image[:, :, 3]
        mask = alpha_channel > 0
        image[mask, 0:3] = 255
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 將圖片轉換為遮罩
        ret, mask=cv2.threshold(gray, 127, 255, 0)
        # 提取多邊形輪廓
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # 選擇最大的輪廓
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            polygon = max_contour.squeeze().tolist()
            polygon = ''.join([f" {point[0]/width} {point[1]/height}" for point in polygon])
            return max_contour, polygon
        else:
            return None, None

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
    
