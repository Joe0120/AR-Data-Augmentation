import bpy, json
import sys
sys.path.insert(0,r'.')
from Camera import Camera
from BlenderEnv import BlenderEnv
from ObjGenerator import ObjGenerator
from BBOX import BBOX
import utils
from itertools import product

if __name__ == '__main__':
    with open("config_setting.json", encoding="utf-8") as json_file:
        config_setting = json.load(json_file)
    blender_env = BlenderEnv(config_setting)
    blender_env.set_env()
    blender_env.init_node()
    blender_env.remove_all_obj()

    Camera(config_setting).set_camera()

    generator = ObjGenerator(config_setting)
    generator.create_collection()
    
    bbox = BBOX(config_setting)

    material_ls = utils.get_material_ls()
    for material in material_ls:
        material = generator.load_obj(material)

        param_ranges = [config_setting["obj_generate_setting"][param] for param in config_setting["obj_generate_setting"]]
        param_combinations = list(product(*param_ranges))
        param_names = list(config_setting["obj_generate_setting"].keys())
        for param_set in param_combinations:
            param_dict = {param_names[i]: param_set[i] for i in range(len(param_names))}
            print(param_dict)
            
            save_filename = generator.generate(material, param_dict)
            obj_exist_in_img = True
            if config_setting["mode_config"]["mode"]=="2D":
                bbox_2D = bbox.get_bbox_2D(save_filename)
                if bbox_2D:
                    utils.write_yolo_label(save_filename, bbox_2D, config_setting["blender_env"]["resolution"])
                else:
                    obj_exist_in_img = False
                    utils.delete_img(save_filename)
            elif config_setting["mode_config"]["mode"]=="3D":
                print("3D")

            if config_setting["mode_config"]["with_bg"] and obj_exist_in_img:
                utils.merge_bg(save_filename, config_setting["file_env"]["bg_path"], config_setting["blender_env"]["resolution"])

            if (not config_setting["mode_config"]["with_color"]) and obj_exist_in_img:
                utils.convert_to_bw(save_filename)

        blender_env.remove_all_obj()
