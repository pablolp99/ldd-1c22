import json
import time
from typing import Dict

from selenium import webdriver

if __name__ == "__main__":

    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")

    wd = webdriver.Chrome("chromedriver", options=options)
    url = "https://encuestas-finales.exactas.uba.ar/docs.html"
    wd.get(url)

    main_list = wd.find_element_by_xpath("//ul[@class='list']")
    button_xpath = "/html/body/div[4]/div[1]/div[2]/div[1]/span/a"

    docentes: Dict[int, dict] = dict()

    for j in range(122):

        for i, e in enumerate(main_list.find_elements_by_xpath(".//a")):
            idx = i + j * 40
            docentes[idx] = dict()
            docentes[idx][e.text] = e.get_attribute("href")

        print(j, len(docentes.keys()))

        link = wd.find_elements_by_xpath(button_xpath)[-1]
        link.click()
        time.sleep(1)

        main_list = wd.find_element_by_xpath("//ul[@class='list']")

    with open("docentes.json", "w") as write_file:
        json.dump(docentes, write_file, indent=4)
