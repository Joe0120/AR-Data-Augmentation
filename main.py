import bpy, json, sys
from itertools import product
import threading
sys.path.insert(0,r'.')
from Camera import Camera
from BlenderEnv import BlenderEnv
from Material import Material
from BBOX import BBOX
from Display import Display
import utils

if __name__ == '__main__':
    with open("config_setting.json", encoding="utf-8") as json_file:
        config_setting = json.load(json_file)
    blender_env = BlenderEnv(config_setting)
    blender_env.set_env()
    blender_env.init_node()
    blender_env.remove_all_obj()
    blender_env.create_collection()

    Camera(config_setting).set_camera()

    bbox = BBOX(config_setting)

    display, event = Display(), threading.Event()
    display_thread = threading.Thread(target=display.start_mjpeg_server, args=(event,))
    display_thread.daemon = True
    display_thread.start()
    display.generate_frame('waiting...')

    material_ls: [Material] = utils.get_material_ls(config_setting)
    for material in material_ls:
        material.load_obj()

        param_ranges = [config_setting["obj_generate_setting"][param] for param in config_setting["obj_generate_setting"]]
        param_combinations = list(product(*param_ranges))
        param_names = list(config_setting["obj_generate_setting"].keys())
        for param_set in param_combinations:
            param_dict = {param_names[i]: param_set[i] for i in range(len(param_names))}
            print(param_dict)
            material.render_material(param_dict)
            obj_exist_in_img = True
            if config_setting["mode_config"]["mode"]=="2D":
                bbox_2D = bbox.get_bbox_2D(material.save_filename)
                if bbox_2D:
                    utils.write_yolo_label(material.save_filename, bbox_2D, config_setting["blender_env"]["resolution"])
                else:
                    obj_exist_in_img = False
                    utils.delete_img(material.save_filename)
            elif config_setting["mode_config"]["mode"]=="3D":
                print("3D")

            if config_setting["mode_config"]["with_bg"] and obj_exist_in_img:
                utils.merge_bg(material.save_filename, config_setting["file_env"]["bg_path"], config_setting["blender_env"]["resolution"])

            if (not config_setting["mode_config"]["with_color"]) and obj_exist_in_img:
                utils.convert_to_bw(material.save_filename)

            display.generate_frame(material.save_filename)
        blender_env.remove_all_obj()
    event.set()
