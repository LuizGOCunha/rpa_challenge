from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup

from constants import SECTION_XPATH_DICT, NYT


class InfoGetter:
    nyc = NYT
    sectiondict = SECTION_XPATH_DICT

    def __init__(self, query="senate", section="new york", months=5) -> None:
        self.query = query
        self.section = section
        self.months = months
        self.html_query = None

    def wait_until_find_xpath(self, driver, xpath):
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def get_query_html(self):
        driver = webdriver.Firefox()
        driver.get(f"https://www.nytimes.com/search?query={self.query}")

        cookie_x_path = "/html/body/div/div[2]/main/div[2]/div[1]/div/div[2]/button"
        self.wait_until_find_xpath(driver, cookie_x_path)
        cookie_x = driver.find_element(By.XPATH, value=cookie_x_path)
        cookie_x.click()

        section_path = "/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/button/label"
        self.wait_until_find_xpath(driver, section_path)
        section = driver.find_element(By.XPATH, value=section_path)
        section.click()

        self.wait_until_find_xpath(driver, self.sectiondict[self.section])
        section = driver.find_element(By.XPATH, value=self.sectiondict[self.section]) 
        section.click()
        html = driver.page_source

        driver.close()

        bs = BeautifulSoup(html, features="lxml")
        self.html_query = bs.prettify()
        return self.html_query

    def get_list_of_articles_urls(self):
        if self.html_query:
            soup = BeautifulSoup(self.html_query, features="lxml")
            anchors = soup.find_all("a")
            links_list = []
            for tag in anchors:
                if tag.has_attr("href"):
                    link = tag.attrs["href"]
                    has_date_length = len(link) > 10
                    starts_with_date = self.is_date(link[0:12])
                    if has_date_length and starts_with_date:
                        link = tag.attrs["href"]
                        links_list.append(link)
            article_list = []
            for link in links_list:
                article = self.nyc + link  
                article_list.append(article)
            return article_list
    
    def is_date(self, string:str):
        elements = list(filter(lambda x: x != "",string.split("/")))
        has_three_items = len(elements) == 3
        if has_three_items:
            has_correct_lengths = len(elements[0]) == 4 and len(elements[1]) == 2 and len(elements[2]) == 2
            if has_correct_lengths:
                return True
        return False



if __name__ == "__main__":

    getter = InfoGetter("senate", "blogs", 5)
    getter.get_query_html()
    getter
        


