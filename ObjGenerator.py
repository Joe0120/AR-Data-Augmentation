import bpy
import os, datetime
import math

class ObjGenerator():
    def __init__(self, config_setting):
        self.config_setting = config_setting

    def create_collection(self):
        for name in ['fbx_col', 'blend_col']:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
        return

    def load_obj(self, material):
        if material['type'] == 'fbx':
            bpy.ops.import_scene.fbx(filepath = material['path'])
            obj = bpy.context.selected_objects[0]
            bpy.data.collections['fbx_col'].objects.link(obj)
            material['obj'] = bpy.data.objects[obj.name]

        elif self.config_setting["mode_config"]["mode"]=="2D" and material['type']=='blend':
            blendFile = material['path']
            with bpy.data.libraries.load(blendFile) as (data_from, data_to):
                data_to.collections = data_from.collections
            instance = bpy.data.objects.new(data_to.collections[0].name, None)
            instance.instance_type = 'COLLECTION'
            instance.instance_collection = data_to.collections[0]
            bpy.data.collections['blend_col'].objects.link(instance)
            material['obj'] = bpy.data.objects[data_to.collections[0].name]

        elif self.config_setting["mode_config"]["mode"]=="3D" and material['type']=='blend':
            blendFile = material['path']
            link = False # append, set to true to keep the link to the original file
            with bpy.data.libraries.load(blendFile, link=link) as (data_from, data_to):
                data_to.collections = data_from.collections
            for coll in data_to.collections:
                if coll is not None: bpy.data.collections['blend_col'].children.link(coll)
                material['obj'] = bpy.data.objects[data_to.collections[0].name]

        return material

    def generate(self, material, param_dict):
        material['obj'].location.x = param_dict['location_x']
        material['obj'].location.y = param_dict['location_y']
        material['obj'].location.z = param_dict['location_z']
        material['obj'].rotation_euler.x = math.radians(param_dict['rotation_x'])
        material['obj'].rotation_euler.y = math.radians(param_dict['rotation_y'])
        material['obj'].rotation_euler.z = math.radians(param_dict['rotation_z'])

        output_filename = f"{material['category']} {material['name']} " + \
                        f"{round(param_dict['location_x'],2)} {round(param_dict['location_y'],2)} {round(param_dict['location_z'],2)} " + \
                        f"{round(param_dict['rotation_x'],2)} {round(param_dict['rotation_y'],2)} {round(param_dict['rotation_z'],2)} " + \
                        f"{str(datetime.datetime.now().timestamp()).replace('.', '')}"

        save_filename = os.path.abspath(self.config_setting["file_env"]["save_file"]) +'/'+ output_filename
        print(save_filename)
        bpy.context.scene.render.filepath = save_filename if(self.config_setting["file_env"]["save_file"]) else os.path.join(self.out_dir_path,'temp')
        bpy.ops.render.render(write_still=True)

        return save_filename