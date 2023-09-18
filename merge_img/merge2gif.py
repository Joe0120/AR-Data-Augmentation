from PIL import Image
import os, re
background='BSIS_2'
project='BSIS_2'

filenames = next(os.walk(f'result/{project}/'), (None, None, []))[2]  # [] if no file

# 打开所有PNG图像并将它们添加到一个列表中
images = []
for file_name in filenames:
    img = Image.open(f'result/{project}/{file_name}')
    images.append(img)

# 保存为GIF动画
output_gif = f'result/{project}.gif'
images[0].save(output_gif, save_all=True, append_images=images[1:], duration=800, loop=0)

# 清理打开的图像对象
for img in images:
    img.close()

print(f'GIF动画已保存为 {output_gif}')
