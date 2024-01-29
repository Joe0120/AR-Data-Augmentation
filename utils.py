import os, json, glob, cv2, re
import numpy as np
from math import sqrt
import numpy as np
import random
from PIL import Image
from typing import Union
from Material import Material

def get_material_ls(config_setting):
    material_ls = []
    for category in os.listdir('objects'):
        fbx_dir = os.path.abspath(r'objects/{}/*.fbx'.format(category))
        blend_dir = os.path.abspath(r'objects/{}/*.blend'.format(category))
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

def write_yolo_label(filename, bbox_2D, img_size):
    # sample: bbox_2D = [(x_min,y_min), (x_max,y_max)]
    x = (bbox_2D[0][0] + bbox_2D[1][0]) / (2 * img_size[0])
    y = (bbox_2D[0][1] + bbox_2D[1][1]) / (2 * img_size[1])
    w = (bbox_2D[1][0] - bbox_2D[0][0]) / img_size[0]
    h = (bbox_2D[1][1] - bbox_2D[0][1]) / img_size[1]
    content = f"0 {x} {y} {w} {h}"
    write_file(filename, content)
    return

def write_kitti_label(filename, bev_alpha, bbox_2D, dimension, bbox_3D_loc, bev_rotation_y):
    content = f"Car 0.00 0 {round(bev_alpha, 4)} {bbox_2D[0][0]} {bbox_2D[0][1]} {bbox_2D[1][0]} {bbox_2D[1][1]} {round(dimension[2], 4)} {round(dimension[0], 4)} {round(dimension[1], 4)} {bbox_3D_loc[0]} {bbox_3D_loc[1]} {bbox_3D_loc[2]} {round(bev_rotation_y, 4)}"
    
    write_file(filename.replace("image_2", "label_2"), content)
def write_polygon_label(filename, polygon):
    content = f"0{polygon}"
    write_file(filename, content)
    return

def write_kitti_calib(filename):
    content = '''P0: 7.215377000000e+02 0.000000000000e+00 6.095593000000e+02 0.000000000000e+00 0.000000000000e+00 7.215377000000e+02 1.728540000000e+02 0.000000000000e+00 0.000000000000e+00 0.000000000000e+00 1.000000000000e+00 0.000000000000e+00
P1: 7.215377000000e+02 0.000000000000e+00 6.095593000000e+02 -3.875744000000e+02 0.000000000000e+00 7.215377000000e+02 1.728540000000e+02 0.000000000000e+00 0.000000000000e+00 0.000000000000e+00 1.000000000000e+00 0.000000000000e+00
P2: 689.6903 -0.0001 621.0000 -0.0001 0.0000 689.6903 187.5000 343.5957 0.0000 -0.0000 1.0000 -0.0000
P3: 7.215377000000e+02 0.000000000000e+00 6.095593000000e+02 -3.395242000000e+02 0.000000000000e+00 7.215377000000e+02 1.728540000000e+02 2.199936000000e+00 0.000000000000e+00 0.000000000000e+00 1.000000000000e+00 2.729905000000e-03
R0_rect: 9.999239000000e-01 9.837760000000e-03 -7.445048000000e-03 -9.869795000000e-03 9.999421000000e-01 -4.278459000000e-03 7.402527000000e-03 4.351614000000e-03 9.999631000000e-01
Tr_velo_to_cam: 7.533745000000e-03 -9.999714000000e-01 -6.166020000000e-04 -4.069766000000e-03 1.480249000000e-02 7.280733000000e-04 -9.998902000000e-01 -7.631618000000e-02 9.998621000000e-01 7.523790000000e-03 1.480755000000e-02 -2.717806000000e-01
Tr_imu_to_velo: 9.999976000000e-01 7.553071000000e-04 -2.035826000000e-03 -8.086759000000e-01 -7.854027000000e-04 9.998898000000e-01 -1.482298000000e-02 3.195559000000e-01 2.024406000000e-03 1.482454000000e-02 9.998881000000e-01 -7.997231000000e-01
'''
    write_file(filename.replace("image_2", "calib"), content)

def merge_bg(filename, bg_path, img_size):
    bg_img = (Image.open(bg_path)).resize(img_size, Image.LANCZOS)
    obj_img = (Image.open(f'{filename}.png')).resize(img_size, Image.LANCZOS)
    bg_img.paste(obj_img, (0,0), mask=obj_img)
    bg_img.save(f'{filename}.png')
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

def multi_bbox_2D(mask, img_size, cat_ls):
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
        bbox_ls += f"0 {x} {y} {w} {h}\n"
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
            polygon_ls+=f"0{polygon}\n"
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
            cat = re.search(r'[\\\/](\w+)\ \w+\ [\d+\-]', random_elements_ls[idx]).group(1)
            if not merge and not mask:
                merge = Image.open(random_elements_ls[idx])
                mask = np.where(np.array(merge)[:, :, 3] != 0, 1, 0)
                cat_ls.append(cat)
        
            new_merge_mask, back_area = merge_mask(mask, random_elements_ls[idx+1])
            if back_area>0.15:
                mask = new_merge_mask
                merge = merge_img(merge, random_elements_ls[idx+1], img_size=img_size)
                cat_ls.append(cat)

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
