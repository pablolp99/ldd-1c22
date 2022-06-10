import json
import re
from io import BytesIO
import time

import numpy as np
import pandas as pd
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By

import logging
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PIXELS = {
    0: (13, 13),
    1: (42, 13),
    2: (71, 13),
    3: (100, 13),
    4: (129, 13),
    5: (158, 13),
    6: (187, 13),
    7: (216, 13),
    8: (245, 13),
    9: (274, 13),
    10: (303, 13),
    11: (332, 13),
    12: (361, 13),
    13: (390, 13),
    14: (419, 13),
    15: (448, 13),
}

with open("avg_colors.json", "r") as f:
    data = json.load(f)

COLORS_DICT = data
COLORS_DF = pd.DataFrame([COLORS_DICT]).T

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

    docs = pd.read_csv("doc_results.csv")
    courses = docs[['course','course_url']].drop_duplicates()

    course_results = pd.DataFrame()

    for idx, r in courses.iterrows():

        wd.get(r.course_url)

        # Show only color scale
        wd.find_element(By.XPATH, '//*[@id="nb"]/div[2]/div/span[1]/a[2]').click()

        table = wd.find_elements(By.XPATH, "//table[@class='inline']//tr")[1:]

        course_terms = []

        for i in range(0, len(table), 3):
            wd.execute_script(f"window.scrollTo(0, {i*100})")
            _tmp = pd.Series()
            try:

                survey = table[i]

                students = int(re.search(
                    r"(\d*)\salumnos", survey.find_element(By.XPATH, ".//td[@class='cur']").text
                ).group(1))
                m = re.search(
                    r"(2c|1c|v)(\d{4})", survey.find_elements(By.XPATH, ".//td")[0].text
                )
                term = m.group(1)
                year = m.group(2)

                logger.info(f"{idx} - {r.course} - {i/3} - {term} / {year}")


                img_url = survey.find_element(By.XPATH, ".//img").get_attribute("src")
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                pixels = img.load()

                course_survey = []
                for q, p in PIXELS.items():
                    result = float(
                        COLORS_DF.apply(
                            lambda x: np.linalg.norm(np.array(x[0]) - np.array(pixels[p])),
                            axis=1,
                        ).idxmin()
                    )
                    course_survey.append(result)
                
                
                details = survey.find_element(By.XPATH, ".//span[@class='small']//a[2]").get_attribute("href")
                comment_button = survey.find_element(By.XPATH, ".//span[@class='small']//a[3]")
                comment_button.click()
                time.sleep(0.2)

                comments_table = table[i+2]
                comments = comments_table.find_elements(By.XPATH, ".//div[@class='comment']//div[@class='cm']")
                comments = list(map(lambda c: c.text.strip(), comments))
                comment_button.click()

                _tmp['course'] = r.course
                _tmp['course_id'] = hash(f"{r.course}{term}{year}")
                _tmp['course_url'] = r.course_url
                _tmp['year'] = year
                _tmp['term'] = term
                _tmp['survey'] = course_survey
                _tmp['details'] = details
                _tmp['comments'] = comments
                course_terms.append(_tmp)
            except Exception as e:
                logger.info(f"{idx} - {r.course} - {i/3} Failed to be scraped")
        
        if not _tmp.empty:
            course_terms = pd.concat(course_terms)
            course_results = pd.concat([course_results, course_terms]).reset_index(drop=True)
            course_results.to_csv("courses_results.csv")
