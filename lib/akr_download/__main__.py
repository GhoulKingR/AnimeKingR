__version__ = '0.2.3'

import argparse
from akr_extensions import Extension

def main():
    try:
        parser = argparse.ArgumentParser(
            description="A simple anime bot for downloading your favorite animes.",
            prog="akr-download"
        )
        parser.add_argument("-v", "--version", action="store_true", help="Display the software version of this anime bot")
        parser.add_argument("-d", "--debug", action="store_true", help="Display browser activity, and enable terminal logging")
        parser.add_argument("anime_name", nargs='?', help="Search for the anime you want to download")

        args = parser.parse_args()

        version = args.version
        debug = args.debug
        anime_name = args.anime_name

        animepahe = Extension(debug)

        if version:
            print(f"v{__version__}")
            return
                
        if anime_name != None: animepahe.run(anime_name)
        else: parser.print_help()
    except KeyboardInterrupt:
        print("\nExiting program...")

if __name__ == "__main__":
    main()
