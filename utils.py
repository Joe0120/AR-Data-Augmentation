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

def write_kitti_label(filename, bev_alpha, bbox_2D, dimension, bbox_3D_loc, bev_rotation_y):
    content = f"Car 0.00 0 {round(bev_alpha, 4)} {bbox_2D[0][0]} {bbox_2D[0][1]} {bbox_2D[1][0]} {bbox_2D[1][1]} {round(dimension[2], 4)} {round(dimension[0], 4)} {round(dimension[1], 4)} {bbox_3D_loc[0]} {bbox_3D_loc[1]} {bbox_3D_loc[2]} {round(bev_rotation_y, 4)}"
    
    write_file(filename.replace("image_2", "label_2"), content)
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