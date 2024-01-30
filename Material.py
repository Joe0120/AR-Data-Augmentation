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
            for coll in data_to.collections:
                if coll is not None: bpy.data.collections['blend_col'].children.link(coll)
                self.obj = bpy.data.objects[data_to.collections[0].name]

    def set_args(self, args):
        self.args = args

    def setting_place(self):
        self.obj.location.x = self.args['location_x']
        self.obj.location.y = self.args['location_y']
        self.obj.location.z = self.args['location_z']
        self.obj.rotation_euler.x = math.radians(self.args['rotation_x'])
        self.obj.rotation_euler.y = math.radians(self.args['rotation_y'])
        self.obj.rotation_euler.z = math.radians(self.args['rotation_z'])

    def name_save_filename(self, filename=None):
        if filename:
            save_filename = os.path.abspath(self.config_setting["file_env"]["save_file"]) +'/image_2/'+ filename
            self.save_filename = save_filename
            print(save_filename)
        else:
            output_filename = f"{self.category} {self.name} " + \
                            f"{round(self.args['location_x'],2)} {round(self.args['location_y'],2)} {round(self.args['location_z'],2)} " + \
                            f"{round(self.args['rotation_x'],2)} {round(self.args['rotation_y'],2)} {round(self.args['rotation_z'],2)} " + \
                            f"{str(datetime.datetime.now().timestamp()).replace('.', '')}"

            save_filename = os.path.abspath(self.config_setting["file_env"]["save_file"]) +'/'+ output_filename
            self.save_filename = save_filename
