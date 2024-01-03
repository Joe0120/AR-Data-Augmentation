import os, json, glob, cv2
import numpy as np
from PIL import Image
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

def merge_bg(filename, bg_path, img_size):
    bg_img = (Image.open(bg_path)).resize(img_size, Image.LANCZOS)
    obj_img = (Image.open(f'{filename}.png')).resize(img_size, Image.LANCZOS)
    bg_img.paste(obj_img, (0,0), mask=obj_img)
    bg_img.save(f'{filename}.png')
    return

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