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
        segmentation_mask = cv2.imread(filename+'.png')
        segmentation_mask = cv2.cvtColor(segmentation_mask,cv2.COLOR_BGR2GRAY)
        
        if(np.sum(segmentation_mask) == 0): return None

        rows, cols = np.where(segmentation_mask != 0)            
        x_min, x_max = np.min(cols), np.max(cols) 
        y_min, y_max = np.min(rows), np.max(rows)
        width, length = x_max-x_min, y_max-y_min
        if (width < self.config_setting["mode_config"]["smallest_obj_size"][0]) or (length < self.config_setting["mode_config"]["smallest_obj_size"][1]): 
            return None
        return [(x_min,y_min), (x_max,y_max)]
    
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
    
