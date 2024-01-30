import os, json, glob, cv2, re
import numpy as np
from math import sqrt
import numpy as np
import random
from PIL import Image
from typing import Union
from Material import Material

def get_category_ls(config_setting):
    class_path = config_setting["file_env"]["classes"]
    with open(class_path, "r") as file:
        category_ls = [line.strip() for line in file.readlines()]
    return category_ls

def get_material_ls(config_setting, category_ls):
    material_ls = []
    for category in category_ls:
        fbx_dir = os.path.abspath(f'objects/{category}/*.fbx')
        blend_dir = os.path.abspath(f'objects/{category}/*.blend')
        for obj_path in glob.glob(fbx_dir)+glob.glob(blend_dir):
            material_ls.append(Material(config_setting, category, obj_path))
    return material_ls

def write_file(filename, content):
    with open(filename+'.txt', 'w') as f:
        f.write(content)
    return

def delete_img(filename):
    os.remove(filename+'.png')
    return

def find_class_from_filename(filename):
    file_name = os.path.splitext(os.path.basename(filename))[0]
    first_part = file_name.split(' ')[0]

    with open('config_setting.json','r') as config_file:
        config_data = json.load(config_file)
    # class_path = "class.txt" 
    class_path = config_data.get('classes','class.txt')

    with open(class_path, 'r') as f:
        class_mapping = {class_name.strip(): index for index, class_name in enumerate(f.readlines())}
        class_name = class_mapping.get(first_part, "None")
        return class_name


def write_yolo_label(filename, bbox_2D, img_size):
    class_name = find_class_from_filename(filename)

    # print(f"File: {filename}, Class Index: {class_name}")
    x = (bbox_2D[0][0] + bbox_2D[1][0]) / (2 * img_size[0])
    y = (bbox_2D[0][1] + bbox_2D[1][1]) / (2 * img_size[1])
    w = (bbox_2D[1][0] - bbox_2D[0][0]) / img_size[0]
    h = (bbox_2D[1][1] - bbox_2D[0][1]) / img_size[1]
    content = f"{class_name} {x} {y} {w} {h}"
    write_file(filename, content)
    return

def write_polygon_label(filename, polygon):
    content = f"0{polygon}"
    write_file(filename, content)
    return

def merge_img(front_img_name:Union[str, Image.Image], back_img_name:Union[str, Image.Image], img_size=(1280, 720), save_img_name=None) ->  Image.Image:
    front_img = front_img_name if isinstance(front_img_name, Image.Image) else Image.open(front_img_name)
    back_img = back_img_name if isinstance(back_img_name, Image.Image) else Image.open(back_img_name)
    front_img = front_img.resize(img_size, Image.LANCZOS).convert('RGBA')
    back_img = back_img.resize(img_size, Image.LANCZOS).convert('RGBA')

    back_img = Image.alpha_composite(back_img, front_img)
    if save_img_name: back_img.save(save_img_name)

    return back_img

def convert_to_bw(filename):
    color_image = Image.open(f'{filename}.png')
    bw_image = color_image.convert("LA")
    bw_image.save(f'{filename}.png')
    return

def saveToJson(ls, filename):
    json_object = json.dumps(ls, indent=4, ensure_ascii=False)
    with open(filename, "w", encoding="utf-8") as outfile:
        outfile.write(json_object)

def fisheye_remove_edge(mask_filename:str, filename:str, img_size:list):
    # 魚眼去掉黑邊
    mask = np.array(cv2.resize(cv2.imread(mask_filename, cv2.IMREAD_UNCHANGED), img_size))
    render_image = np.array(cv2.imread(filename+'.png', cv2.IMREAD_UNCHANGED))

    alpha_mask = mask[:, :, 3] > 0
    render_image[alpha_mask] = [0, 0, 0, 0]

    cv2.imwrite(filename+'.png', render_image)

def multi_bbox_2D(mask, img_size, cat_ls, class_mapping):
    bbox_ls = ''
    unique_values = np.unique(mask)
    if None in unique_values: return None
    for val in unique_values:
        if val == 0: continue
        non_zero_pixels = np.argwhere(mask == val)
        left_top = non_zero_pixels.min(axis=0)
        right_bottom = non_zero_pixels.max(axis=0)

        bbox_2D = [tuple(left_top[::-1]), tuple(right_bottom[::-1])]
        
        x = (bbox_2D[0][0] + bbox_2D[1][0]) / (2 * img_size[0])
        y = (bbox_2D[0][1] + bbox_2D[1][1]) / (2 * img_size[1])
        w = (bbox_2D[1][0] - bbox_2D[0][0]) / img_size[0]
        h = (bbox_2D[1][1] - bbox_2D[0][1]) / img_size[1]

        cat_label = class_mapping.get(find_class_from_filename(cat_ls), "Unknown")
        bbox_ls += f"{cat_label} {x} {y} {w} {h}\n"
    return bbox_ls

def multi_polygon(mask, target_size, cat_ls):
    polygon_ls = ''
    unique_values = np.unique(mask)
    if None in unique_values: return None
    for val in unique_values:
        if val == 0: continue
        region = np.uint8(mask == val) * 255
        contours, _ = cv2.findContours(region, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            polygon = max_contour.squeeze().tolist()
            polygon = ''.join([f" {point[0]/target_size[0]} {point[1]/target_size[1]}" for point in polygon])
            polygon_ls+=f"{cat_ls}{polygon}\n"
    return polygon_ls

def merge_mask(front_img_name:Union[str, np.ndarray], back_img_name:Union[str, np.ndarray]) -> np.ndarray:
    front_img = front_img_name if type(front_img_name) == np.ndarray else np.array(Image.open(front_img_name))
    back_img = back_img_name if type(back_img_name) == np.ndarray else np.array(Image.open(back_img_name))
    
    front_mask = front_img if len(front_img.shape) < 3 else np.where(front_img[:, :, 3] != 0, 1, 0)
    back_mask = back_img if len(back_img.shape) < 3 else np.where(back_img[:, :, 3] != 0, 1, 0)

    next = front_mask.max()+1
    merge = np.where(front_mask > 0, front_mask, np.where(back_mask > 0, next, 0))

    ori_back_area = np.sum(back_mask == 1)
    merge_back_area = np.sum(merge == next)
    # print(next, ", back_area:", merge_back_area/ori_back_area, "%")
    return merge, merge_back_area/ori_back_area

def sort_position(img_ls:list) -> list:
    sorted_img_ls = sorted(
        img_ls,
        key=lambda path: sqrt(float(os.path.basename(path).split(' ')[2])**2 + float(os.path.basename(path).split(' ')[3])**2)
    )
    seen_values, unique_img_ls = set(), []
    for path in sorted_img_ls :
        val = ' '.join(os.path.basename(path).split(' ')[2:4])
        if val not in seen_values:
            seen_values.add(val)
            unique_img_ls.append(path)
    return unique_img_ls

def merge_multi_obj(mode, save_file, img_size, min, max, bg_img):
    img_ls = [file for file in glob.glob(save_file + r'/*.png') if 'fisheye_' not in file]

    for i in range(0, len(img_ls)//min*2):
        random_number = random.randint(min, max)
        random_elements_ls = sort_position(random.sample(img_ls, random_number))

        cat_ls = []
        merge, mask= None, None
        for idx in range(len(random_elements_ls) - 1):
            print(random_elements_ls[idx])
            
            if not merge and not mask:
                cat = re.search(r'[\\\/](\w+)\ \w+\ [\d+\-]', random_elements_ls[idx]).group(1)
                merge = Image.open(random_elements_ls[idx])
                mask = np.where(np.array(merge)[:, :, 3] != 0, 1, 0)
                cat_ls.append(cat)
                print("-----------------")
                print("append", cat)
        
            new_merge_mask, back_area = merge_mask(mask, random_elements_ls[idx+1])
            if back_area>0.15:
                cat = re.search(r'[\\\/](\w+)\ \w+\ [\d+\-]', random_elements_ls[idx+1]).group(1)
                mask = new_merge_mask
                merge = merge_img(merge, random_elements_ls[idx+1], img_size=img_size)
                cat_ls.append(cat)
                print("append", cat)
                print("------------------")

        print("==================")
        print(cat_ls)
        print("==================")

        if mode == '2D':
            label = multi_bbox_2D(mask, img_size, cat_ls)
        elif mode == 'Segmentation':
            label = multi_polygon(mask, img_size, cat_ls)

        if label:
            if bg_img: merge = merge_img(merge, bg_img, img_size=img_size)

            merge.save(f'{save_file}/multi_obj/{i:0>6}.png')
            with open(f'{save_file}/multi_obj/{i:0>6}.txt', 'w') as f: f.write(label)

def create_render_folder(config_setting):
    create_folder_ls = []
    if config_setting["mode_config"]["mode"]=="KITTI_3D":
        create_folder_ls += ["/image_2", "/label_2", "/calib"]
    if config_setting["mode_config"]["multi_obj"]["enable"]:
        create_folder_ls += ["/multi_obj"]
    for folder in create_folder_ls:
        save_file = os.path.abspath(config_setting["file_env"]["save_file"] + folder)
        if not os.path.exists(save_file): os.makedirs(save_file)
