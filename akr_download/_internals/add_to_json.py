import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
json_file = "extensions.json"
file_path  = os.path.join(script_dir, json_file)
json_data = json.load(open(file_path, 'r'))


extension = sys.argv[1]
json_data.append(extension)

json.dump(json_data, open(file_path, 'w'))