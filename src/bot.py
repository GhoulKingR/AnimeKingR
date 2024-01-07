from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from tqdm import tqdm
import time
import math
import requests

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
    
    ans = int(input(f"There are {total_episodes} episodes, which do you want to downlad? "))
    if 0 < ans and ans <= total_episodes:
        return ans
    else:
        return ask_episode()

def get_episode_link(episode):
    total = anime_details['total']
    for i in range(0, math.ceil(total/30)):
        beginning = total - (i * 30)
        end = total - ((i * 30) + 29)
        if end <= episode and episode <= beginning:
            driver.get(f"https://animepahe.ru/anime/{jsonres['data'][choice-1]['session']}?page={i+1}")
            time.sleep(1)
            a = driver.find_elements(By.CSS_SELECTOR, ".episode-list-wrapper .play")[beginning - episode]
            return a.get_attribute("href")

def which_quality():
    time.sleep(1)
    qualities = []

    for a in driver.find_elements(By.CSS_SELECTOR, "#pickDownload .dropdown-item"):
        quality = {
            "name": a.get_attribute("innerHTML").split(" ")[2],
            "link": a.get_attribute("href")
        }
        qualities.append(quality)

    text = "Qualities found:\n"
    text += "\n".join([
        f"{i+1}. {qualities[i]['name']}"
        for i in range(len(qualities))
    ]) + "\n\n"
    text += "Your answer: "
    ans = int(input(text)) - 1

    if 0 <= ans and ans < len(qualities):
        return qualities[ans]["link"]
    else:
        return which_quality()


if __name__ == "__main__":
    # Prepare driver
    service = Service(executable_path="./geckodriver")
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(service=service, options=options)

    # Open site
    driver.get("https://animepahe.ru")

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
    for i in range(1, 6):
        try:
            a = driver.find_element(By.XPATH, "//a[text()='Continue']")
            link_to_download = a.get_attribute("href")
            driver.get(link_to_download)
            break
        except:
            print(f"{i}/{5} retries, waiting 3s")
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