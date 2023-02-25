from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook, load_workbook
import re

from constants import SECTION_XPATH_LIST, NYT


class InfoGetter:
    """class created to facilitate the job of getting and parsing information from
    a number of NYT articles based on a determined number of variables"""
    nyc = NYT
    sectionlist = SECTION_XPATH_LIST

    def __init__(self, query:str="senate", section:int=1, months:int=5) -> None:
        self.query = query
        self.section = section
        self.months = months
        self.html_query = None
        self.article_list = None
        self.parsed_info = None

    def wait_until_find_xpath(self, driver:webdriver.Firefox, xpath:str) -> None:
        '''Receives a driver and an xpath, making the driver wait only the necessary time
        to find the given element'''
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def get_list_of_possible_sections(self, ps_html:str):
        # We could create this method to get the list of possible sections, return to user and have him choose
        # However, this could be against the spirit of automation in the first place
        pass

    def get_query_html(self) -> str:
        '''Method used to create the html_query variable (None by default). This variable corresponds to
        the page source of the query page, after one applys the query and the section appropriately'''
        driver = webdriver.Firefox()
        driver.get(f"https://www.nytimes.com/search?query={self.query}")

        cookie_x_path = "/html/body/div/div[2]/main/div[2]/div[1]/div/div[2]/button"
        self.wait_until_find_xpath(driver, cookie_x_path)
        cookie_x = driver.find_element(By.XPATH, value=cookie_x_path)
        cookie_x.click()

        section_path = "/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/button/label"
        self.wait_until_find_xpath(driver, section_path)
        # return sections to user and have him choose
        section = driver.find_element(By.XPATH, value=section_path)
        section.click()

        self.wait_until_find_xpath(driver, self.sectionlist[self.section])
        section = driver.find_element(By.XPATH, value=self.sectionlist[self.section]) 
        section.click()
        html = driver.page_source

        driver.close()

        bs = BeautifulSoup(html, features="lxml")
        self.html_query = bs.prettify()
        return self.html_query

    def get_list_of_articles_urls(self) -> list:
        '''returns the list of all articles present in the query page. If the html_query object variable
        was not created, will raise an error.'''
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
            self.article_list = article_list
            return article_list
        elif self.html_query is None:
            raise ValueError("HTML Query variable not yet created")
        elif self.html_query == "":
            raise NameError("HTML Query is empty")
        else:
            raise ValueError("HTML query variable is unavailable")

    def turn_datestring_into_datelist(self, datestring:str) -> list:
        '''receives a string of dates separated by "/". returns a list of all numbers between the "/"
        with no empty strings.'''
        elements = list(filter(lambda x: x != "",datestring.split("/")))
        return elements
    
    def is_date(self, string:str) -> bool:
        '''Checks a string and returns a boolean that indicates if the string obeys the pattern of a date'''
        # After thought: regex is probably a better solution
        elements = self.turn_datestring_into_datelist(string)
        has_three_items = len(elements) == 3
        if has_three_items:
            has_correct_lengths = len(elements[0]) == 4 and len(elements[1]) == 2 and len(elements[2]) == 2
            if has_correct_lengths:
                return True
        return False

    def filter_article_links(self) -> list:
        '''checks the dates of all articles gathered, allows to remain only the ones inside
        the permissible amount of months based on the months variable'''
        new_article_list = []
        if self.article_list:
            for article_link in self.article_list:
                article_date = self.get_date_from_link(article_link)
                date_is_appropriate = self.check_if_date_is_appropriate(article_date)
                if date_is_appropriate:
                    new_article_list.append(article_link)
            self.article_list = new_article_list
            return self.article_list
        elif self.article_list == []:
            raise ValueError("Article list is empty")
        elif self.article_list is None: 
            raise NameError("Article List not yet created")
        else:
            raise ValueError("Article list unavailable")
    
    def check_if_date_is_appropriate(self, date:date) -> bool:
        '''returns a bool that indicates if the date is permissible based on the
        months variable'''
        today = datetime.today().date()
        maximum_date = today - relativedelta(months=self.months)
        if date >= maximum_date:
            return True
        if date < maximum_date:
            return False

    def get_date_from_link(self, link:str) -> date:
        '''Gather the date present in the received article link and returns it'''
        link = link.replace(NYT, "")
        datestring = link[:12]
        liststring = self.turn_datestring_into_datelist(datestring)
        year = int(liststring[0])
        month = int(liststring[1])
        day = int(liststring[2])
        article_date = date(year, month, day)
        return article_date

    def get_html_from_url(self, url:str) -> str:
        '''uses Selenium to get the html of an aticle link, quickly opening the page 
        to get the source and immediately closing it'''
        driver = webdriver.Firefox()
        driver.get(url)
        html = driver.page_source
        driver.close()
        return html

    def get_title_from_html(self, html:str) -> str:
        '''receives an articel html, gathers the headline inside it then returns it'''
        bs = BeautifulSoup(html, features="lxml")
        headers = bs.find_all("h1")
        for header in headers:
            if header.has_attr("data-testid"):
                if header.attrs["data-testid"] == "headline":
                    headline = header.text
                    return headline
        return None

    def get_description_from_html(self, html:str) -> str:
        '''gather the description from an article html and returns it'''
        bs = BeautifulSoup(html, features="lxml")
        description = bs.find(id="article-summary")
        if description:
            description = description.text
            return description
        else: 
            return None

    def get_image_link_from_html(self, html:str) -> str:
        '''gather the image_link from an article and returns it'''
        bs = BeautifulSoup(html, features="lxml")
        picture = bs.find("picture")
        img_source = picture.findChild("img").attrs["src"]
        return img_source
    
    def check_money_on_html(self, html:str) -> bool:
        '''check if inside the article exists a pattern that matches probable ways
        of referring to money in dollars, returning a boolean based on that'''
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

    def get_article_info_from_url(self, link:str) -> dict:
        '''Gets gathering methods in one single method so it can get all relevant info of an article
        and returning it in the form of a dictionary'''
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
    
    def create_info_list(self) -> list:
        '''gather all relevant info on our available list of articles. Returns parsed info'''
        self.get_query_html()
        self.get_list_of_articles_urls()
        self.filter_article_links()
        self.parsed_info = list(map(self.get_article_info_from_url, self.article_list))
        return self.parsed_info
    
    def create_info_excel(self):
        '''Creates an excel file based on the parsed information of our articles. Raises error if 
        parsed_info variable was not yet created.'''
        if self.parsed_info:
            wb = Workbook()
            ws = wb.active
            ws.title = "Article Info"

            ws.append(['url', 'title', 'date', 'description', 'picture filename', 'search appearances', 'mentions money'])
            for article in self.parsed_info:
                ws.append(list(article.values()))

            wb.save("articleinfo.xlsx")

        elif self.parsed_info == []:
            raise ValueError("Parsed list is empty")
        elif self.parsed_info is None:
            raise NameError("Parsed Info not yet created")
        else: 
            raise ValueError("Parsed list unavailable")


if __name__ == "__main__":
    getter = InfoGetter("senate", "blogs", 5)
    getter.get_query_html()
    getter
        
'https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1'

