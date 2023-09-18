import os, re, cv2
import numpy as np

def format_fisheye_img(img_path):
    mask = np.array(cv2.resize(cv2.imread('fisheye_mask/BSIS_2.png', cv2.IMREAD_UNCHANGED), [1280, 720]))
    render_image = np.array(cv2.imread(img_path, cv2.IMREAD_UNCHANGED))

    alpha_mask = mask[:, :, 3] > 0
    render_image[alpha_mask] = [0, 0, 0, 0]

    return render_image

def yolo2elan(annotation, split_pixel=40):
    img_size = (1280,720)
    cls_id,x,y,w,h = annotation.split(' ')
    cv_coord = int(float(x)*img_size[0]),int(float(y)*img_size[1])
    return int(cv_coord[0] // (1280/split_pixel)),int(cv_coord[1]//(720/split_pixel)), [x,y,w,h]
    #return cv2.rectangle(img,cv_min,cv_max,(255,0,0),2)


def create_folder_structure(node, parent_path):
    for key, values in node.items():
        folder_path = os.path.join(parent_path, key)
        os.makedirs(folder_path, exist_ok=True)
        for value in values:
            file_path = os.path.join(folder_path, value)
            os.makedirs(file_path, exist_ok=True)
            os.makedirs(file_path+'/img', exist_ok=True)
            os.makedirs(file_path+'/txt', exist_ok=True)
        if isinstance(values, dict):
            create_folder_structure(values, folder_path)

def generate_filestructure(classes):
    pattern = re.compile(r'([a-zA-Z]+)(\d+)')
    result = {}
    for _class in classes:
        match = pattern.match(_class)
        if match:
            key = match.group(1)
            value = match.group(0)
            if key not in result: result[key] = []
            result[key].append(value)
    return result

def generate_RVS_filestructure(cat_ls):
    result = {}
    for cat in cat_ls:
        cat = cat.split('/')[-1]
        sub_cat, model = cat.split(' ')
        main_cat = re.search(r'([a-zA-Z\-]+)(\d+)', sub_cat).group(1)
        if main_cat not in result: result[main_cat] = []
        result[main_cat].append(f'{model}')
    return result