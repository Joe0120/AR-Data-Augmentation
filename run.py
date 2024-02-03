import os, sys, json, datetime
from PIL import Image

filename = sys.argv[1:][0]
filename = filename if '.json' in filename else f'{filename}.json'
with open(f"config/{filename}", encoding="utf-8") as json_file:
    cus_config = json.load(json_file)

# print(cus_config["blender_env"])
# "NOT_NULL" 不能是 null, 如果是null會報錯
# "OPTIONAL" 可以是 null, 如果是null會使用預設值
# "CONDITIONAL" 符合條件才可以是 null, 會自動填上預設值
# args: [rule, default_value, [[condition element], [condition, condition value]]]
default_config = {
    "file_env": {
        "save_file": ["OPTIONAL", f"output/{str(datetime.datetime.now().timestamp()).replace('.', '')}"],
        "blender_file": ["OPTIONAL", None],
        "bg_path": ["CONDITIONAL", None, [["mode_config", "with_bg"], ["==", False]]],
        "classes": ["OPTIONAL", None],
        "kitti_calib_file": ["CONDITIONAL", None, [["mode_config", "mode"], ["!=", "KITTI_3D"]]],
    },
    "mode_config": {
        "mode": ["NOT_NULL"],
        "with_bg": ["OPTIONAL", True],
        "with_color": ["OPTIONAL", True],
        "is_fisheye": ["OPTIONAL", False],
        "display_bbox": ["OPTIONAL", True],
        "display_bg": ["OPTIONAL", True],
        "smallest_obj_size": ["OPTIONAL", [15, 15]],
        "multi_obj": {
            "enable": ["NOT_NULL"],
            "max_obj": ["OPTIONAL", 5],
            "min_obj": ["OPTIONAL", 3]
        }
    },
    "blender_env": {
        "background_blender": ["OPTIONAL", True],
        "resolution": ["CONDITIONAL", "get_img_size", [["file_env", "bg_path"], ["==", "NOT_NULL"]]],
        "cam_distance": ["OPTIONAL", 200],
        "cam_location": ["OPTIONAL", None],
        "cam_rotation": ["OPTIONAL", None],
        "cam_intrinsics": ["OPTIONAL", None]
    },
    "obj_generate_setting": {
        "location_x": ["OPTIONAL", [10]],
        "location_y": ["OPTIONAL", [-5, 0, 5]],
        "location_z": ["OPTIONAL", [0]],
        "rotation_x": ["OPTIONAL", [0]],
        "rotation_y": ["OPTIONAL", [0]],
        "rotation_z": ["OPTIONAL", [0, 90, 180, 270]]
    }
}

VALID_CONFIG = True
def alert(msg, color="red"):
    color_code = {
        "red": "\033[91m",
        "yellow": "\033[93m",
        "yellow1": "\033[0m",
    }
    if color == "red":
        global VALID_CONFIG
        VALID_CONFIG = False
    print(f"{color_code[color]}{msg}\033[0m")

def traverse_dict(d, path=[]):
    for key, value in d.items():
        current_path = path + [key]
        if isinstance(value, dict):
            traverse_dict(value, current_path)
        else:
            check_rule(current_path, value)

def get_value_by_path(current_dict, path):
    for key in path:
        if key in current_dict:
            current_dict = current_dict[key]
        else:
            return "NOT_EXIST"
    return current_dict

def update_value_by_path(d, keys, new_value):
    if len(keys) == 1:
        if keys[0] not in d:
            d[keys[0]] = new_value
        else:
            d[keys[0]] = new_value
    elif keys[0] in d:
        update_value_by_path(d[keys[0]], keys[1:], new_value)
    else:
        d[keys[0]] = {}
        update_value_by_path(d[keys[0]], keys[1:], new_value)

def check_rule(path, default_rule):
    cus_value = get_value_by_path(cus_config, path)
    if cus_value == None or cus_value == "NOT_EXIST" or cus_value == "":
        if default_rule[0] == "NOT_NULL":
            if cus_value == "NOT_EXIST" or cus_value == None:
                alert(f"Error: {path} is not allowed to be null", "red")
        elif default_rule[0] == "OPTIONAL":
            if cus_value == "NOT_EXIST" or cus_value == None:
                update_value_by_path(cus_config, path, default_rule[1])
                alert(f"Warning: {path} using default value: {default_rule[1]}", "yellow")
        elif default_rule[0] == "CONDITIONAL":
            target_value = get_value_by_path(cus_config, default_rule[2][0])
            if default_rule[2][1][0] == "==" and target_value == default_rule[2][1][1]:
                pass
            elif default_rule[2][1][0] == "!=" and target_value != default_rule[2][1][1]:
                pass
            elif  default_rule[2][1][0] == "==" and default_rule[2][1][1] == "NOT_NULL" and target_value != "NOT_EXIST" and target_value:
                pass
            else:
                alert(f"Error: Because of {default_rule[2][0]} condition, {path} is not allowed to be null or not exist", "red")

            if VALID_CONFIG and default_rule[1] == "get_img_size":
                img_size = list(Image.open(target_value).size)
                update_value_by_path(cus_config, path, img_size)
                alert(f"Warning: {path} using default value: {img_size}", "yellow")
            else:
                update_value_by_path(cus_config, path, default_rule[1])
                alert(f"Warning: {path} using default value: {default_rule[1]}", "yellow")
    return

traverse_dict(default_config)

if VALID_CONFIG:
    print(cus_config)
    with open("config_setting.json", "w", encoding="utf-8") as json_file:
        json.dump(cus_config, json_file, indent=4)
else:
    sys.exit()

print("Running...........")
run_script = 'blender'
if cus_config["blender_env"]["background_blender"]:
    run_script += ' --background'
if cus_config["file_env"]["blender_file"]:
    run_script += f' {cus_config["file_env"]["blender_file"]}'
run_script += f' --python main.py'
os.system(run_script)
# os.system(f'blender --background {cus_config["file_env"]["blender_file"]} --python {cus_config["file_env"]["python_file"]}')
print("\n\nDone!")