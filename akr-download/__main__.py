__version__ = '0.2.3'

from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time
import math
import requests
import argparse
from akr_extensions import AnimeExtension

class AnimePahe(AnimeExtension):
    
    def search(self, anime_name):
        response = requests.get(f"https://animepahe.ru/api?m=search&q={anime_name}")
        if response.status_code == 200:
            # Print the response content (usually in JSON format for APIs)
            self.jsonres = response.json()
            # print(jsonres)
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")

    def list_anime(self):
        animes = [
            f"{i+1}. {self.jsonres['data'][i]['title']}"
            for i in range(len(self.jsonres['data']))
        ]

        print(
            "Animes:\n" +
            "\n".join(animes) + "\n\n"
        )

    def get_anime_details(self):
        # Prepare driver
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        
        if not self._debug:
            options.add_argument("--headless")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self._driver = webdriver.Chrome(options=options)
        
        # Set anime details
        response = requests.get(
            f"https://animepahe.ru/api?m=release&id={self.jsonres['data'][self._choice-1]['session']}&sort=episode_desc&page=1"
        )
        self.anime_details = response.json()
    
    def get_episode(self): # This will cover other things until the download
        # Get episode link
        episode = self._ask_episode()
        episode_link = self._get_episode_link(episode)
        self._driver.get(episode_link)

        # Get quality lists
        quality_link = self._which_quality()
        self._driver.get(quality_link)

    def download_episode(self):
        # Get link from continue button
        print("Downloading...")
        print("Please wait for it to begin...")
        for i in range(1, 6):
            try:
                a = self._driver.find_element(By.XPATH, "//a[text()='Continue']")
                link_to_download = a.get_attribute("href")
                self._driver.get(link_to_download)
                break
            except:
                # print(f"{i}/{5} retries, waiting 3s")
                time.sleep(3)

        # find download link and token
        link = self._driver.find_element(By.CSS_SELECTOR, ".main .download form").get_attribute("action")
        token = self._driver.find_element(By.CSS_SELECTOR, ".main .download form input").get_attribute("value")
        
        # Preper header and payload
        cookies = '; '.join([
            f"{cookie['name']}={cookie['value']}"
            for cookie in self._driver.get_cookies()
        ])
        data = {
            "_token": token
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Referer': 'https://kwik.cx/f/r6gCLSqIe9Nh',
            'Origin': 'https://kwik.cx',
            'Host': 'kwik.cx',
            'Cookie': cookies
        }

        # Download anime
        response = requests.post(link, data=data, headers=headers, stream=True)
        file_name = response.headers.get('Content-Disposition').split('=')[1]
        self.download_to_file(response, file_name)

    def quit(self):    # Close anything it needs to
        self._driver.quit()

    def _ask_episode(self):
        total_episodes = self.anime_details['total']
        
        ans = int(input(f"There are {total_episodes} episodes, which do you want to download? "))
        if 0 < ans and ans <= total_episodes:
            return ans
        else:
            return self._ask_episode()
    
    def _get_episode_link(self, episode):
        page = math.ceil(episode/30)
        response = requests.get(f"https://animepahe.ru/api?m=release&id={self.jsonres['data'][self._choice-1]['session']}&sort=episode_asc&page={page}").json()
        position = (episode - (page - 1) * 30) - 1
        return f"https://animepahe.ru/play/{self.jsonres['data'][self._choice-1]['session']}/{response['data'][position]['session']}"


    def _which_quality(self):
        time.sleep(1)
        qualities = []

        for a in self._driver.find_elements(By.CSS_SELECTOR, "#pickDownload .dropdown-item"):
            quality_text = a.get_attribute("innerText").split(" ")
            sub_dub = 'dub' if quality_text[-1] == 'eng' else 'sub'
            quality = quality_text[2]
            size = quality_text[3][1:-1]
            quality = {
                "name": f"{quality}{' ' * (15 - len(quality))}{size}{' ' * (15 - len(size))}{sub_dub}",
                "link": a.get_attribute("href")
            }
            qualities.append(quality)

        text = "\nHere are qualities found:\n"
        text += "\n".join([
            f"{i+1}. {qualities[i]['name']}"
            for i in range(len(qualities))
        ]) + "\n\n"
        text += "Which one do you want to download: "
        ans = int(input(text)) - 1

        if 0 <= ans and ans < len(qualities):
            return qualities[ans]["link"]
        else:
            return self._which_quality()



def main():
    global jsonres
    global choice
    global driver
    global anime_details

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

        animepahe = AnimePahe(debug)

        if version:
            print(f"v{__version__}")
            return
                
        if anime_name != None:
            animepahe.search(anime_name)
            animepahe.list_anime()
            animepahe.get_anime_choice()
            animepahe.get_anime_details()
            animepahe.get_episode()
            animepahe.download_episode()
            animepahe.quit()
        else: parser.print_help()
    except KeyboardInterrupt:
        print("\nExiting program...")

if __name__ == "__main__":
    main()
