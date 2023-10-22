import bpy, json, sys, os
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
    if config_setting["mode_config"]["is_fisheye"]:
        print(os.path.abspath(f'{config_setting["file_env"]["save_file"]}/fisheye_.png'))
        blender_env.render(os.path.abspath(f'{config_setting["file_env"]["save_file"]}/fisheye_.png'))

    display, event = Display(frame_WH=config_setting["blender_env"]["resolution"]), threading.Event()
    display_thread = threading.Thread(target=display.start_mjpeg_server, args=(event,))
    display_thread.daemon = True
    display_thread.start()
    display.generate_frame(text='waiting...')

    material_ls: [Material] = utils.get_material_ls(config_setting)
    cnt=0
    for material in material_ls:
        material.load_obj()

        param_ranges = [config_setting["obj_generate_setting"][param] for param in config_setting["obj_generate_setting"]]
        param_combinations = list(product(*param_ranges))
        param_names = list(config_setting["obj_generate_setting"].keys())
        for param_set in param_combinations:
            param_dict = {param_names[i]: param_set[i] for i in range(len(param_names))}
            print(param_dict)
            material.set_args(param_dict)
            material.setting_place()
            material.name_save_filename(f"{cnt:0>6}")
            cnt+=1
            blender_env.render(material.save_filename)

            obj_exist_in_img = True

            if config_setting["mode_config"]["is_fisheye"] and obj_exist_in_img:
                utils.fisheye_remove_edge(f'{config_setting["file_env"]["save_file"]}/fisheye_.png', material.save_filename)

            if config_setting["mode_config"]["mode"]=="2D":
                bbox_2D = bbox.get_bbox_2D(material.save_filename)
                if bbox_2D:
                    utils.write_yolo_label(material.save_filename, bbox_2D, config_setting["blender_env"]["resolution"])
                else:
                    obj_exist_in_img = False
                    utils.delete_img(material.save_filename)
            elif config_setting["mode_config"]["mode"]=="3D":
                if material.name == "car_1":
                    material_info = {"length":5.13,"width":2.28,"height":1.99}
                elif material.name == "car_2":
                    material_info = {"length":4.26,"width":2.17,"height":1.76}
                elif material.name == "car_3":
                    material_info = {"length":5.78,"width":2.51,"height":1.78}
                bbox_2D = bbox.get_bbox_2D(material.save_filename)
                bbox_3D = bbox.get_bbox_3D()
                if len(bbox_2D) and len(bbox_3D):
                    bbox_3D_loc = bbox.get_bbox3D_loc(bbox_3D, material_info)
                    bev_alpha = bbox.get_bev_alpha(material.args)
                    bev_rotation_y = bbox.get_bev_rotation_y(material.args)
                    print(bev_alpha, bbox_2D, bbox_3D_loc, bev_rotation_y)
                    utils.write_kitti_label(material.save_filename, bev_alpha, bbox_2D, material_info, bbox_3D_loc, bev_rotation_y)
                    utils.write_kitti_calib(material.save_filename)
                print("3D")

            if config_setting["mode_config"]["with_bg"] and obj_exist_in_img:
                utils.merge_bg(material.save_filename, config_setting["file_env"]["bg_path"], config_setting["blender_env"]["resolution"])

            if (not config_setting["mode_config"]["with_color"]) and obj_exist_in_img:
                utils.convert_to_bw(material.save_filename)

            if obj_exist_in_img:
                if config_setting["mode_config"]["mode"]=="2D":
                    display.generate_frame(img_path=material.save_filename, bbox=["2D", bbox_2D])
        blender_env.remove_all_obj()
    display.generate_frame(text="Done !")
    event.set()
