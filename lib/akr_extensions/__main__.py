import argparse
import os
from . import add_to_json, list_extensions, remove_from_json

parser = argparse.ArgumentParser(prog="akr-extensions", description="Add, list, remove, and set default extensions for AnimeKingR")
parser.add_argument("command", help='Command can either be "add", "list", "set-default", or "remove"')
parser.add_argument("extension", nargs='?', help='The extension that you want to install')

args = parser.parse_args()
command = args.command
extension = args.extension

match command:
    case "add":
        if type(extension) == str:
            add_to_json.main(extension)
        else:
            raise argparse.ArgumentError(message="Expected an option for extension")
    case "list":
        list_extensions.main()
    case "remove":
        if type(extension) == str:
            remove_from_json.main(extension)
        else:
            raise argparse.ArgumentError(message="Expected an option for extension")
    case "set-default":
        if type(extension) == str:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            json_file = "__init__.py"
            file_path  = os.path.join(script_dir, json_file)
            file = open(file_path, 'w')
            file.write(f"from {extension} import Extension")
        else:
            raise argparse.ArgumentError(message="Expected an option for extension")
        