from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from bs4 import BeautifulSoup

from constants import SECTION_XPATH_DICT, NYT


class InfoGetter:
    nyc = NYT
    sectiondict = SECTION_XPATH_DICT

    def __init__(self, query, section, months) -> None:
        self.query = query
        self.section = section
        self.months = months
        self.get_query_html()

    
    def get_query_html(self):
        driver = webdriver.Firefox()
        driver.get(f"https://www.nytimes.com/search?query={self.query}")
        sleep(1)
        cookie_x = driver.find_element(By.XPATH, value="/html/body/div/div[2]/main/div[2]/div[1]/div/div[2]/button")
        cookie_x.click()
        sleep(0.5)
        section = driver.find_element(By.XPATH, value="/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/button/label")
        section.click()
        sleep(0.5)
        section = driver.find_element(By.XPATH, value=self.sectiondict[self.section]) 
        section.click()
        sleep(0.5)
        html = driver.page_source

        bs = BeautifulSoup(html, features="lxml")
        self.html_query = bs.prettify()



if __name__ == "__main__":

    getter = InfoGetter("senate", "blogs", 5)
        


