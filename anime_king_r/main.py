__version__ = '0.2.0'

from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time
import math
import requests
import argparse

jsonres = None
choice = None
driver = None
anime_details = None

def list_anime():
    animes = [
        f"{i+1}. {jsonres['data'][i]['title']}"
        for i in range(len(jsonres['data']))
    ]

    print(
        "Animes:\n" +
        "\n".join(animes) + "\n\n"
    )

def get_choice():
    return int(input("Your choice (0 to search again): "))

def ask_episode():
    total_episodes = anime_details['total']
    
    ans = int(input(f"There are {total_episodes} episodes, which do you want to download? "))
    if 0 < ans and ans <= total_episodes:
        return ans
    else:
        return ask_episode()

def get_episode_link(episode):
    page = math.ceil(episode/30)
    response = requests.get(f"https://animepahe.ru/api?m=release&id={jsonres['data'][choice-1]['session']}&sort=episode_asc&page={page}").json()
    position = (episode - (page - 1) * 30) - 1
    return f"https://animepahe.ru/play/{jsonres['data'][choice-1]['session']}/{response['data'][position]['session']}"

def which_quality():
    time.sleep(1)
    qualities = []

    for a in driver.find_elements(By.CSS_SELECTOR, "#pickDownload .dropdown-item"):
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
        return which_quality()


def main():
    global jsonres
    global choice
    global driver
    global anime_details

    try:
        parser = argparse.ArgumentParser(description="A simple anime bot for downloading your favorite animes.")
        parser.add_argument("-v", "--version", action="store_true", help="Display the software version of this anime bot")
        parser.add_argument("-d", "--debug", action="store_true", help="Display browser activity, and enable terminal logging")

        args = parser.parse_args()

        version = args.version
        debug = args.debug

        if version:
            print(f"v{__version__}")
        else:
            # Prepare driver
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            
            if not debug:
                options.add_argument("--headless")

            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            driver = webdriver.Chrome(options=options)

            # Search for anime
            while True:
                search = input("Search: ")
                response = requests.get(f"https://animepahe.ru/api?m=search&q={search}")
                if response.status_code == 200:
                    # Print the response content (usually in JSON format for APIs)
                    jsonres = response.json()
                    # print(jsonres)
                else:
                    # Print an error message if the request was not successful
                    print(f"Error: {response.status_code} - {response.text}")
                
                list_anime()
                choice = get_choice()

                if choice != None and choice > 0:
                    break
            
            # Set anime details
            response = requests.get(
                f"https://animepahe.ru/api?m=release&id={jsonres['data'][choice-1]['session']}&sort=episode_desc&page=1"
            )
            anime_details = response.json()
            
            # Get episode link
            episode = ask_episode()
            episode_link = get_episode_link(episode)
            driver.get(episode_link)

            # Get quality lists
            quality_link = which_quality()
            driver.get(quality_link)

            # Get link from continue button
            print("Downloading...")
            print("Please wait for it to begin...")
            for i in range(1, 6):
                try:
                    a = driver.find_element(By.XPATH, "//a[text()='Continue']")
                    link_to_download = a.get_attribute("href")
                    driver.get(link_to_download)
                    break
                except:
                    # print(f"{i}/{5} retries, waiting 3s")
                    time.sleep(3)

            # find download link and token
            link = driver.find_element(By.CSS_SELECTOR, ".main .download form").get_attribute("action")
            token = driver.find_element(By.CSS_SELECTOR, ".main .download form input").get_attribute("value")
            
            # Preper header and payload
            cookies = '; '.join([
                f"{cookie['name']}={cookie['value']}"
                for cookie in driver.get_cookies()
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
            print(file_name)

            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte

            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

            with open(file_name, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

            progress_bar.close()
            driver.quit()
            print("Download complete!")
    except KeyboardInterrupt:
        print("\nExiting program...")

if __name__ == "__main__":
    main()
