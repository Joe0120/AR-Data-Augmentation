import os, json, glob, cv2
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

def write_polygon_label(filename, polygon):
    content = f"0{polygon}"
    write_file(filename, content)
    return

def merge_img(front_img_name:Union[str, Image.Image], back_img_name:Union[str, Image.Image], img_size=(1280, 720), save_img_name=None) ->  Image.Image:
    front_img = front_img_name if type(front_img_name) == Image.Image else Image.open(front_img_name)
    back_img = back_img_name if type(back_img_name) == Image.Image else Image.open(back_img_name)
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

def fisheye_remove_edge(mask_filename, filename):
    # 魚眼去掉黑邊
    mask = np.array(cv2.resize(cv2.imread(mask_filename, cv2.IMREAD_UNCHANGED), [1280, 720]))
    render_image = np.array(cv2.imread(filename+'.png', cv2.IMREAD_UNCHANGED))

    alpha_mask = mask[:, :, 3] > 0
    render_image[alpha_mask] = [0, 0, 0, 0]

    cv2.imwrite(filename+'.png', render_image)

def multi_bbox_2D(mask, img_size):
    bbox_ls = ''
    unique_values = np.unique(mask)
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

def multi_polygon(mask, target_size):
    unique_values = np.unique(mask)
    polygon_ls = ''
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
    img_ls = glob.glob(save_file + r'/*.png')
    if not os.path.exists(save_file+'/multi_obj'): os.makedirs(save_file+'/multi_obj')

    for i in range(0, len(img_ls)//min*2):
        random_number = random.randint(min, max)
        random_elements_ls = sort_position(random.sample(img_ls, random_number))
        merge, mask=None, None

        for idx in range(len(random_elements_ls) - 1):        
            if not merge and not mask:
                mask = random_elements_ls[idx]
                merge = random_elements_ls[idx]
        
            new_merge_mask, back_area = merge_mask(mask, random_elements_ls[idx+1])
            if back_area>0.15:
                mask = new_merge_mask
                merge = merge_img(merge, random_elements_ls[idx+1], img_size=img_size)
        if mode == '2D':
            label = multi_bbox_2D(mask, img_size)
        elif mode == 'Segmentation':
            label = multi_polygon(mask, img_size)
        if bg_img:
            merge = merge_img(merge, bg_img, img_size=img_size)
        merge.save(f'{save_file}/multi_obj/{i:0>6}.png')
        with open(f'{save_file}/multi_obj/{i:0>6}.txt', 'w') as f: f.write(label)
