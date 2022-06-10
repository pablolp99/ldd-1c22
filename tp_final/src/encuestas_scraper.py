import json
import re
from io import BytesIO

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
    # wd.set_page_load_timeout(5)

    with open("docentes.json", "r") as file:
        docentes = json.load(file)

    doc_results = pd.DataFrame(
        columns=[
            "doc_name",
            "term",
            "year",
            "student_count",
            "course",
            "course_id",
            "course_url",
            "doc_survey",
        ]
    )

    idx_doc = 0
    total_doc = len(docentes.keys())
    for k, v in docentes.items():

        doc_name = list(v.keys())[0]
        survey_results = v[doc_name]

        try:
            wd.get(survey_results)
        except:
            logger.warn(f"Professor: {doc_name} failed to be downloaded")
            
            file_object = open('fallos.txt', 'a')
            file_object.write(f'{doc_name}  {idx_doc}\n')
            file_object.close()
            continue

        # Click to get only colors:
        wd.find_elements(By.XPATH, "//span[@class='nbtype']//a")[1].click()

        doc_data = wd.find_elements(By.XPATH, "//table[@class='inline']//tr")[2:]
        # El par docente-materia comienza en los indices 0 y 1
        # Luego salta de a 4 y 5, asi continua.

        tmp_df = pd.DataFrame(
            columns=[
                "doc_name",
                "term",
                "year",
                "student_count",
                "course",
                "course_id",
                "course_url",
                "doc_survey",
            ]
        )

        for i in range(0, len(doc_data), 4):

            logger.info(f"{idx_doc}/{total_doc} - {(100 * idx_doc/total_doc):.3f}% - {doc_name} - {i/4}")

            # Encuesta docente: i
            # Materia: i+1
            survey = doc_data[i]
            course = doc_data[i + 1]

            try:
                m = re.search(r"((2c|1c|v)(\d{4}))\s(\d*)", survey.text)

                term = m.group(2)
                year = m.group(3)
                student_count = m.group(4)
                course_name = course.text.strip()

                img_url = survey.find_element(By.XPATH, ".//img").get_attribute("src")

                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                pixels = img.load()

                doc_survey = []
                for q, p in PIXELS.items():

                    result = float(
                        COLORS_DF.apply(
                            lambda x: np.linalg.norm(np.array(x[0]) - np.array(pixels[p])),
                            axis=1,
                        ).idxmin()
                    )
                    doc_survey.append(result)

                _tmp = pd.Series()
                _tmp["doc_name"] = doc_name
                _tmp["term"] = term
                _tmp["year"] = year
                _tmp["student_count"] = student_count
                _tmp["course"] = course_name
                _tmp["course_id"] = hash(f"{course_name}{term}{year}")
                _tmp["course_url"] = course.find_element(By.XPATH, ".//a").get_attribute(
                    "href"
                )
                _tmp["doc_survey"] = doc_survey
                tmp_df = tmp_df.append(_tmp, ignore_index=True)

            except Exception as e:
                logger.warn(f"Professor: {doc_name} failed to be downloaded")
                
                file_object = open('fallos.txt', 'a')
                file_object.write(f'{doc_name}  {idx_doc}\n')
                file_object.close()
                continue

        if not tmp_df.empty:
            doc_results = pd.concat([doc_results, tmp_df]).reset_index(drop=True)
            doc_results.to_csv("doc_results.csv")

        idx_doc += 1