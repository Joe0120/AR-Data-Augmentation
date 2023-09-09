import os
import json

with open("config_setting.json", encoding="utf-8") as json_file:
    config_setting = json.load(json_file)
print(config_setting)
print("Running...........")

# os.system(f'blender --background {config_setting["file_env"]["blender_file"]} --python {config_setting["file_env"]["python_file"]}')
# os.system(f'blender {config_setting["file_env"]["blender_file"]}')
# os.system(f'blender --python {config_setting["file_env"]["python_file"]}')
os.system(f'blender --background --python test_BBOX.py')

print("\n\nDone!")