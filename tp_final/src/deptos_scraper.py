import json
import re
from io import BytesIO
import time

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

import logging
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://encuestas-finales.exactas.uba.ar/deptos.html"

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

    wd.get(BASE_URL)

    df_courses = pd.DataFrame()

    deptos = wd.find_elements(By.XPATH, "//ul[@class='list']//li")

    dd = dict()

    for depto in deptos:
        area = depto.find_elements(By.XPATH, ".//a")[0]
        area_url = area.get_attribute("href")
        area_name = area.text
        dd[area_name] = area_url

    for k in dd.keys():
        area_url = dd[k]
        area_name = k
        
        wd.get(area_url)
        try:
            pages = int(wd.find_elements(By.XPATH, "//div[@class='list'][1]//a")[-1].text)
            wd.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[2]/div/a[1]").click()
            course_names = [list(map(lambda c: c.text, wd.find_elements(By.XPATH, "//ul[@class='list']")[0].find_elements(By.XPATH, ".//li")))]            
            np = wd.find_elements(By.XPATH, "//div[@class='list'][1]//span[@class='right']//a")

            idx = 1
            while len(np) >= 1 and idx != pages:
                logger.info(f"{area_name} - {idx}")
                np[-1].click()
                time.sleep(0.1)

                course_names.append(list(map(lambda c: c.text, wd.find_elements(By.XPATH, "//ul[@class='list']")[0].find_elements(By.XPATH, ".//li"))))
                np = wd.find_elements(By.XPATH, "//div[@class='list'][1]//span[@class='right']//a")
                idx += 1

        except:
            course_names = [list(map(lambda c: c.text, wd.find_elements(By.XPATH, "//ul[@class='list']")[0].find_elements(By.XPATH, ".//li")))]

        course_names = [k for i in course_names for k in i]
        df = pd.DataFrame(course_names)
        df['departamento'] = area_name

        df_courses = pd.concat([df_courses, df])
        df_courses.to_csv("deptos_cursos.csv")
        wd.get(BASE_URL)
    
    breakpoint()
    print(len(df_courses))