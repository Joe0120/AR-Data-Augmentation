# AR-Data-Augmentation
## Installation

<details>
<summary><b>Windows</b></summary>

### Install Blender
https://www.blender.org/download/

### Set blender to env PATH
```
C:\Program Files\Blender Foundation\Blender 3.6\
```

### Install pip package into Blender python
```cmd=
cd C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin
python -m pip install blenderproc contourpy cycler fonttools h5py kiwisolver opencv-python packaging Pillow progressbar pyparsing python-dateutil PyYAML six
```
</details>


<details>
<summary><b>Ubuntu</b></summary>

### Install Blender
```
snap install blender --channel=3.6lts/stable --classic
```

### Install pip package into Blender python
```cmd=
cd /snap/blender/current/3.6/python/bin
./python3.10 -m pip install blenderproc contourpy cycler fonttools h5py kiwisolver opencv-python packaging Pillow progressbar pyparsing python-dateutil PyYAML six
```
</details>

### Clone this repo
```cmd=
git clone https://github.com/Joe0120/AR-Augmentation-BBOX-Data-Generator.git
cd AR-Augmentation-BBOX-Data-Generator
```

## Usage
### Place your files into the folder
YOU CAN DOWNLOAD FILES FROM THIS [LINK](https://ntutcc-my.sharepoint.com/:f:/g/personal/111c52017_cc_ntut_edu_tw1/EhNkLiL2fctBsdAoX7XpKjgBuhF_ak6o5ZugSEAsJqERnw?e=9fNlQW)
```
backgrounds/[YOUR_BACKGROUND_HERE].jpg
blender/[YOUR_BLENDER_FILE_HERE].blend
objects/[YOUR_CATEGORY]/[YOUR_MODEL_HERE].fbx
```
You can refer to the file tree below
```
AR-Augmentation-BBOX-Data-Generator
│   .gitignore
│   BBOX.py
│   BlenderEnv.py
│   Camera.py
│   config_setting.json
│   Display.py
│   main.py
│   Material.py
│   ouput.txt
│   README.md
│   run.py
│   utils.py
│   
├───backgrounds
│       [YOUR_BACKGROUND_HERE].jpg
│       
├───blender
│       [YOUR_BLENDER_FILE_HERE].blend
│       
├───conver_format
│   │   BSIS_2.ipynb
│   │   rename.ipynb
│   │   utils.py
│   │   
│   └───result
│           
├───merge_img
│   │   merge2gif.py
│   │   mergeimg.py
│   └───result
│           
├───objects
│   │       
│   ├───[YOUR_CATEGORY]
│   │       [YOUR_MODEL_HERE].fbx
│   ├───car0
│   │       car_1.fbx
│   │       car_2.fbx
│   │       car_3.fbx
│   ├───p1
│   │       walk_kid_1.fbx
│   │       walk_person_1.fbx
│   │       
│   └───yb2
│           bicycle_with_standperson_1.fbx
│           bicycle_with_standperson_2.fbx
│           
└───output
```

### Edit config_setting.json
```json=
{
    "file_env": {
        "save_file": "output/BSIS_2",
        "blender_file": "blender/BSIS_2.blend",
        "bg_path": "backgrounds/BSIS_2.jpg",
        "classes": "clasess.txt",
        "python_file": "main.py"
    },
    "mode_config": {
        "mode": "2D",  // "2D" or "Segmentation"
        "with_bg": false,
        "with_color": true,
        "is_fisheye": true,
        "display_bbox": true,
        "display_bg": true,
        "smallest_obj_size": [15, 15],
        "multi_obj": {
            "enable": true,
            "max_obj": 5,
            "min_obj": 3
        }
    },
    "blender_env": {
        "background_blender": true,
        "resolution": [1280, 720],
        "cam_distance": 200,
        "cam_location": [0, 0, 1.75], // Fill in Camera location [x, y, z] or null
        "cam_rotation": [90, 0, 270] // Fill in Camera rotation [x, y, z] or null
    },
    "obj_generate_setting": {
        "location_x": [1, 3, 5],
        "location_y": [10, 15, 20, 25, -10, -15, -20, -25],
        "location_z": [0],
        "rotation_x": [0],
        "rotation_y": [0],
        "rotation_z": [0, 180]
    }
}
```
### Run the program
```cmd=
python run.py
```
u can view on http://127.0.0.1:8888 realtime
