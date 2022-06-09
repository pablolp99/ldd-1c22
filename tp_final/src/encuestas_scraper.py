import json
import re
import time

from PIL import Image
import requests
from io import BytesIO

from selenium import webdriver

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
    11: (332, 13)
}


if __name__ == '__main__':

    options = webdriver.ChromeOptions()

    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")

    wd = webdriver.Chrome("chromedriver", options=options)
    
    results = dict()

    with open("docentes.json", "r") as file:
        docentes = json.load(file)

    for k, v in docentes.items():

        doc_name = list(v.keys())[0]
        survey_results = v[doc_name]
        
        wd.get(survey_results)
        # Click to get only colors:
        wd.find_elements_by_xpath("//span[@class='nbtype']//a")[1].click()

        doc_data = wd.find_elements_by_xpath("//table[@class='inline']//tr")[2:]
        # El par docente-materia comienza en los indices 0 y 1
        # Luego salta de a 4 y 5, asi continua. 

        for i in range(0, len(doc_data), 4):
            # Encuesta docente: i
            # Materia: i+1
            survey = doc_data[i]
            course = doc_data[i+1]

            m = re.search(r"((2c|1c|v)(\d{4}))\s(\d*)", survey.text)
            
            semester = m.group(2)
            year = m.group(3)
            students = m.group(4)
            course_name = course.text.strip()            

            img_url = survey.find_element_by_xpath(".//img").get_attribute("src")

            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            pixels = img.load()
            
            for q, p in PIXELS.items():
                breakpoint()
                
                print(img[p])

        wd.close()
        exit(0)