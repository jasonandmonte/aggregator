from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import json
from jinja2 import Environment, FileSystemLoader

opts = Options()
opts.add_argument("--headless")
browser = Firefox(options=opts)

environment = Environment(loader=FileSystemLoader("templates/"))
template = environment.get_template("results.html")

posters = {
    "laurelhurst": {
        "now": [],
        "soon": [],
        },
    "bagdad": [],
    "kennedy": [],
}

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

laurelhurst()
mcmenamins("bagdad", "https://www.mcmenamins.com/bagdad-theater-pub/now-playing")
mcmenamins("kennedy", "https://www.mcmenamins.com/kennedy-school/kennedy-school-theater/now-playing")

browser.quit()


now = datetime.now()
# mm/dd/yy H:M:S
dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

output = template.render(date=dt_string, posters=posters)
print(output)