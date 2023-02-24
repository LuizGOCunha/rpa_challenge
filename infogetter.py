from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import re

from constants import SECTION_XPATH_DICT, NYT


class InfoGetter:
    nyc = NYT
    sectiondict = SECTION_XPATH_DICT

    def __init__(self, query="senate", section="new york", months=5) -> None:
        self.query = query
        self.section = section
        self.months = months
        self.html_query = None
        self.article_list = None

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
        else:
            raise NameError

    def turn_datestring_into_datelist(self, datestring:str):
        elements = list(filter(lambda x: x != "",datestring.split("/")))
        return elements
    
    def is_date(self, string:str):
        elements = self.turn_datestring_into_datelist(string)
        has_three_items = len(elements) == 3
        if has_three_items:
            has_correct_lengths = len(elements[0]) == 4 and len(elements[1]) == 2 and len(elements[2]) == 2
            if has_correct_lengths:
                return True
        return False

    def filter_article_links(self):
        new_article_list = []
        if self.article_list:
            for article_link in self.article_list:
                article_date = self.get_date_from_link(article_link)
                date_is_appropriate = self.check_if_date_is_appropriate(article_date)
                if date_is_appropriate:
                    new_article_list.append(article_link)
            self.article_list = new_article_list
            return self.article_list
        else: 
            raise NameError
    
    def check_if_date_is_appropriate(self, date):
        today = datetime.today().date()
        maximum_date = today - relativedelta(months=self.months)
        if date >= maximum_date:
            return True
        if date < maximum_date:
            return False

    def get_date_from_link(self, link:str):
        link = link.replace(NYT, "")
        datestring = link[:12]
        liststring = self.turn_datestring_into_datelist(datestring)
        year = int(liststring[0])
        month = int(liststring[1])
        day = int(liststring[2])
        article_date = date(year, month, day)
        return article_date

    def get_html_from_url(self, url):
        driver = webdriver.Firefox()
        driver.get(url)
        html = driver.page_source
        driver.close()
        return html

    def get_title_from_html(self, html):
        bs = BeautifulSoup(html, features="lxml")
        headers = bs.find_all("h1")
        for header in headers:
            if header.has_attr("data-testid"):
                if header.attrs["data-testid"] == "headline":
                    headline = header.text
                    return headline
        return None

    def get_description_from_html(self, html):
        bs = BeautifulSoup(html, features="lxml")
        description = bs.find(id="article-summary").text
        if description:
            return description
        else: 
            return None

    def get_image_link_from_html(self, html):
        bs = BeautifulSoup(html, features="lxml")
        picture = bs.find("picture")
        img_source = picture.findChild("img").attrs["src"]
        return img_source
    
    def check_money_on_html(self, html):
        # for: number + dollar|dollars|USD
        pattern1 = r"\d+(?:\.\d{1,2})?\s(?:dollars?|USD)"
        # for: $ + number
        pattern2 = r"\$\s?\d+"
        match1 = re.search(pattern1, html)
        match2 = re.search(pattern2, html)
        if match1 or match2:
            return True
        else:
            return False

    def get_article_info_from_url(self, link):
        html = self.get_html_from_url(link)

        title = self.get_title_from_html(html)
        date = self.get_date_from_link(link)
        description = self.get_description_from_html(html)
        pic_filename = self.get_image_link_from_html(html)
        search_appearances = html.count(self.query)
        money_check = self.check_money_on_html(html)

        article_info = {
            "url": link,
            "title": title,
            "date": date.__str__(),
            "description": description,
            "picture filename": pic_filename,
            "search appearances": search_appearances,
            "mentions money": money_check
        }
        return article_info


if __name__ == "__main__":
    getter = InfoGetter("senate", "blogs", 5)
    getter.get_query_html()
    getter
        
'https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1'

