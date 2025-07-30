from selenium import webdriver
from selenium.webdriver.common.by import By

from datetime import datetime
import subprocess
import requests
from bs4 import BeautifulSoup
import json
from jinja2 import Environment, FileSystemLoader

machine = str(subprocess.check_output(['uname', '-m']))

browser = None
if "x86" in machine:
    # wsl2
    from selenium.webdriver import Firefox
    from selenium.webdriver.firefox.options import Options

    opts = Options()
    opts.add_argument("--headless")
    browser = Firefox(options=opts)
else:
    #pi
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_argument("--headless")
    chrome_path = "/usr/local/bin/chromedriver"
    service = Service(chrome_path)
    browser = webdriver.Chrome(service=service, options=opts)

environment = Environment(loader=FileSystemLoader("templates/"))


posters = {
    "laurelhurst": {
        "now": [],
        "soon": [],
        },
    "bagdad": [],
    "kennedy": [],
    "omsi": {
        "after_dark": [],
        "pub": [],
    },
    "portland_art": {
        "title": "",
        "img": ""
    },
    "powells": [],
    "madness": []
}


def cinemagic():
    URL = "https://www.thecinemagictheater.com/coming-attractions"
    browser.get(URL)
    browser.implicitly_wait(5)
    # remove header
    section = browser.find_elements(By.CLASS_NAME, "page-section")[0]
    browser.execute_script("arguments[0].remove();", section)
    browser.implicitly_wait(5)
    header = browser.find_elements(By.CLASS_NAME, "header-announcement-bar-wrapper")[0]
    browser.execute_script("arguments[0].remove();", header)
    
    browser.implicitly_wait(5)
    browser.save_screenshot("assets/cinemagic.png")


def laurelhurst():
    URL = "https://www.laurelhursttheater.com/"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    scripts = soup.find_all("script")
    script = scripts[3]
    json_data = script.string.split("var gbl_movies = ")[1].split("};")[0] + "}"
    movies_data = json.loads(json_data)


    poster_urls = []
    for k in movies_data.keys():
        title = movies_data[k]["title"]
        if "open caption" in title:
            continue
        url = movies_data[k]["posterURL"]
        poster_urls.append(url)

    posters["laurelhurst"]["now"] = poster_urls


def mcmenamins(key: str, url: str):
    # URL = "https://www.mcmenamins.com/kennedy-school/kennedy-school-theater/now-playing"
    browser.get(url)
    browser.implicitly_wait(5)
    now_playing = browser.find_element(By.ID, "MainContent_propertytabs")
    img_list = now_playing.find_elements(By.TAG_NAME, "img")
    
    for img in img_list:
        src = img.get_attribute("src")
        # ignore random site images that are in the main content section
        if "Media/Poster" in src and src not in posters[key]:
            posters[key].append(src)
            

#-------------------------------------------------------------------------------
# Events
#-------------------------------------------------------------------------------

def powells():
    URL = "https://www.powells.com/events"
    browser.get(URL)
    browser.implicitly_wait(5)
    browser.execute_script("window.scrollBy(0, 1000);")
    browser.implicitly_wait(5)
    browser.execute_script("window.scrollBy(0, 1000);")
    browser.implicitly_wait(5)
    cards = browser.find_elements(By.CLASS_NAME, "tw-p-0")

    # We want cards in the future
    for x in range(12,16,1):
        card = cards[x]
        img = card.find_element(By.TAG_NAME, 'img')
        poster = img.get_attribute('src')
        title = card.find_element(By.TAG_NAME, "h3").get_attribute("textContent")
        date = card.find_element(By.CSS_SELECTOR, '[data-test="event-date"]').get_attribute("textContent")
        location = card.find_element(By.CSS_SELECTOR, '[data-test="event-location"]').get_attribute("textContent")
        
        if "Portland, OR 97209" in location:
            location = "City of Books"
        elif "Beaverton, OR 97005" in location:
            location = "Cedar Hills"
        else:
            location = "Oregon"

        posters["powells"].append((poster,title,date,location))
        

def omsi():
    URL = "https://omsi.edu/whats-on/"
    browser.get(URL)
    browser.implicitly_wait(5)
    cards = browser.find_elements(By.CLASS_NAME, "omsi-card__body")
    for card in cards:
        title_list = card.find_elements(By.TAG_NAME, "h4")
        event = (title_list[0].get_attribute("textContent"), title_list[1].get_attribute("textContent"))
        if "Dark" in event[1]:
            # I only want the closest after dark to save space
            if len(posters["omsi"]["after_dark"]) < 1:
                posters["omsi"]["after_dark"].append(event)
        elif "Pub" in event[1]:
            posters["omsi"]["pub"].append(event)
    

def portland_art():
    URL = "https://portlandartmuseum.org/exhibitions/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")
    divs = soup.find_all("div", class_="event-card__featured")
    img = divs[0].find("img")["src"]
    title = divs[0].find("h3", class_="featured-card__title")

    posters["portland_art"]["title"] = title.get_text(strip=True)
    posters["portland_art"]["img"] = img
    

def movie_madness():
    URL = "https://www.moviemadness.org/calendar/"
    browser.get(URL)
    browser.implicitly_wait(5)
    
    cards = browser.find_elements(By.TAG_NAME, "article")
    # TODO: Ingest all cards
    card = cards[0]
    img = card.find_element(By.TAG_NAME, 'img')
    poster = img.get_attribute('src')
    posters["madness"].append(poster)



def _main():
    cinemagic()
    browser.quit()
    

def main():
    laurelhurst()
    mcmenamins("bagdad", "https://www.mcmenamins.com/bagdad-theater-pub/now-playing")
    mcmenamins("kennedy", "https://www.mcmenamins.com/kennedy-school/kennedy-school-theater/now-playing")

    # Events
#    powells()
    omsi()
    portland_art()
    movie_madness()
    cinemagic()
    
    browser.quit()

    now = datetime.now()
    # mm/dd/yy H:M:S
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    
    template = environment.get_template("results.html")
    output = template.render(date=dt_string, posters=posters)
    with open('index.html', 'w') as writer:
        writer.write(output)
    
    template = environment.get_template("events.html")
    output = template.render(date=dt_string, posters=posters)
    with open('events.html', 'w') as writer:
        writer.write(output)

main()
