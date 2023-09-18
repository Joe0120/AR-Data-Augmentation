import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from os import walk
import os, re
background='BSIS_2'
project='BSIS_2'
def brightness_img(pil_image):
    # 增加亮度
    np_image = np.array(pil_image)
    opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGBA2BGRA)
    brightness_factor = 1.2  # +20%
    brightened_image = cv2.convertScaleAbs(opencv_image, alpha=brightness_factor, beta=0)
    return Image.fromarray(cv2.cvtColor(brightened_image, cv2.COLOR_BGRA2RGBA))
def contrast_img(pil_image):
    # 增加对比度
    np_image = np.array(pil_image)
    opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGBA2BGRA)
    contrast_factor = 1.1  # +10%
    contrasted_image = cv2.convertScaleAbs(opencv_image, alpha=contrast_factor, beta=0)
    return Image.fromarray(cv2.cvtColor(contrasted_image, cv2.COLOR_BGRA2RGBA))

target_size = (1280, 720)
filenames = next(walk(f'img/{project}/'), (None, None, []))[2]  # [] if no file
os.makedirs(f'result/{project}', exist_ok=True)

for idx, img in enumerate(filenames):
    print(img)
    if not re.search(r'png|jpg', img): continue
    img1 = (Image.open(f'../backgrounds/{background}.jpg')).resize(target_size, Image.LANCZOS)
    img2 = (Image.open(f'img/{project}/{img}')).resize(target_size, Image.LANCZOS)
    img2 = brightness_img(img2)
    img2 = contrast_img(img2)
    img1.paste(img2, (0,0), mask = img2)
    img1.save(f'result/{project}/{idx}.png')