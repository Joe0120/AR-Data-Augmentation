import os, math, datetime
import bpy

class Material:
    def __init__(self, config_setting, category, obj_path):
        self.config_setting = config_setting
        self.category = category
        self.name = os.path.basename(obj_path).split('.')[0]
        self.type = os.path.basename(obj_path).split('.')[-1]
        self.path = obj_path
        self.args = {
            'location_x': 0,
            'location_y': 0,
            'location_z': 0,
            'rotation_x': 0,
            'rotation_y': 0,
            'rotation_z': 0
        }
        self.obj = None
        self.dimension = [None, None, None]
        self.save_filename = None

    def load_obj(self):
        if self.type == 'fbx':
            bpy.ops.import_scene.fbx(filepath = self.path)
            obj = bpy.context.selected_objects[0]
            bpy.data.collections['fbx_col'].objects.link(obj)
            self.obj = bpy.data.objects[obj.name]
            self.dimension = list(obj.dimensions)

        elif self.type=='blend' and any(mode in self.config_setting["mode_config"]["mode"] for mode in ["2D", "Segmentation"]):
            blendFile = self.path
            with bpy.data.libraries.load(blendFile) as (data_from, data_to):
                data_to.collections = data_from.collections
            instance = bpy.data.objects.new(data_to.collections[0].name, None)
            instance.instance_type = 'COLLECTION'
            instance.instance_collection = data_to.collections[0]
            bpy.data.collections['blend_col'].objects.link(instance)
            self.obj = bpy.data.objects[data_to.collections[0].name]

        elif self.type=='blend' and "3D" in self.config_setting["mode_config"]["mode"]:
            blendFile = self.path
            link = False # append, set to true to keep the link to the original file
            with bpy.data.libraries.load(blendFile, link=link) as (data_from, data_to):
                data_to.collections = data_from.collections
            if data_to.collections[0] is not None: bpy.data.collections['blend_col'].children.link(data_to.collections[0])
            obj = bpy.data.objects[data_to.collections[0].objects[-1].name]
            while obj.parent: obj = obj.parent
            self.obj = obj
            self.dimension = self.get_material_info()

    def get_bbox_3D(self):
        def np_matmul_coords(coords, matrix, space=None):
            M = (space @ matrix @ space.inverted()
            if space else matrix).transposed()
            ones = np.ones((coords.shape[0], 1))
            coords4d = np.hstack((coords, ones))
            return np.dot(coords4d, M)[:,:-1]

        obj_coords_ls = []
        for o in bpy.context.scene.objects:
            if o.type != 'MESH': continue
            obj_coords = np_matmul_coords(np.array(o.bound_box), o.matrix_world.copy())
            if np.all(np.logical_or(obj_coords == 1, obj_coords == -1)): continue
            obj_coords_ls.append(obj_coords)
        coords = np.vstack(tuple(obj_coords_ls))

        bfl = coords.min(axis=0)
        tbr = coords.max(axis=0)
        G  = np.array((bfl, tbr)).T
        bbc = [i for i in itertools.product(*G)]
        return np.array(bbc)

    def get_material_info(self):
        coordinates = self.get_bbox_3D()
        min_x, min_y, min_z = coordinates.min(axis=0)
        max_x, max_y, max_z = coordinates.max(axis=0)
        length = round(max_y - min_y, 6)
        width = round(max_x - min_x, 6)
        # height = round(max_z - min_z, 6)
        height = round(max_z, 6)
        return [width, length, height]
    
    def set_args(self, args):
        self.args = args

    def setting_place(self):
        self.obj.location.x = self.args['location_x']
        self.obj.location.y = self.args['location_y']
        self.obj.location.z = self.args['location_z']
        self.obj.rotation_euler.x = math.radians(self.args['rotation_x'])
        self.obj.rotation_euler.y = math.radians(self.args['rotation_y'])
        self.obj.rotation_euler.z = math.radians(self.args['rotation_z'])

    def name_save_filename(self, filename=None, mode=None):
        output_filename = f"{self.category} {self.name} " + \
                        f"{round(self.args['location_x'],2)} {round(self.args['location_y'],2)} {round(self.args['location_z'],2)} " + \
                        f"{round(self.args['rotation_x'],2)} {round(self.args['rotation_y'],2)} {round(self.args['rotation_z'],2)} " + \
                        f"{str(datetime.datetime.now().timestamp()).replace('.', '')}"
        if mode=="KITTI_3D":
            if filename:
                save_filename = os.path.abspath(self.config_setting["file_env"]["save_file"]) +'/image_2/'+ filename
            else:
                save_filename = os.path.abspath(self.config_setting["file_env"]["save_file"]) +'/image_2/'+ output_filename
            self.save_filename = save_filename
        else:
            save_filename = os.path.abspath(self.config_setting["file_env"]["save_file"]) +'/'+ output_filename
            self.save_filename = save_filename
