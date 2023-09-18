import os
import json

with open("config_setting.json", encoding="utf-8") as json_file:
    config_setting = json.load(json_file)
print(config_setting)
print("Running...........")
run_script = 'blender'
if config_setting["blender_env"]["background_blender"]:
    run_script += ' --background'
if config_setting["file_env"]["blender_file"]:
    run_script += f' {config_setting["file_env"]["blender_file"]}'
run_script += f' --python {config_setting["file_env"]["python_file"]}'
os.system(run_script)
# os.system(f'blender --background {config_setting["file_env"]["blender_file"]} --python {config_setting["file_env"]["python_file"]}')
print("\n\nDone!")