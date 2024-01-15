import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file = "extensions.json"
file_path  = os.path.join(script_dir, json_file)
json_data = json.load(open(file_path, 'r'))

for extension in json_data:
    print(extension)