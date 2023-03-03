from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files

from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary.errors import ElementNotFound
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from datetime import date
from dateutil.relativedelta import relativedelta

from typing import Union, Tuple

import re


class InfoGetter:
    browser = Selenium()
    request = HTTP()
    excel = Files()
    browser.auto_close = False
    article_data = {
                'title': [],
                'date': [],
                'description': [],
                'image': [],
                'query count': [],
                'mentions money': []
            }

    def __init__(self, query="senate",section_numbers:list=[3,6,8], months_ago=1) -> None:
        self.months_ago = months_ago
        self.section_numbers = section_numbers
        self.query = query

    def retrieve_info(self):
        browser = self.browser
        section_numbers = self.section_numbers
        query = self.query

        #get formatted start date
        start_date, end_date = self.get_dates()
        # open browser
        browser.open_available_browser(f"http://www.nytimes.com/search?query={query}&startDate={start_date}&endDate={end_date}")

        # close ad
        browser.click_element('class:css-1qw5f1g')

        # click section dropdown
        browser.click_element("class:css-4d08fs")
        # click sections
        for sn in section_numbers:
            try:
                browser.click_element(f"xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[{sn}]/label/input")
            except ElementNotFound:
                raise ValueError("Section number does not exist")

        #self.adjust_date()

        self.expand_page()

        article_data = self.gather_article_info()

        return article_data
        
    def gather_article_info(self):
        '''Gather data from articles if any results are present. Make sure you are in the results page
        when running this function'''
        r = self.request
        results_div_id = "class:css-46b038"
        self.browser.page_should_contain_element(results_div_id, "CurrentPage is not a Results page")

        articles = self.browser.find_elements('class:css-1l4w6pd')
        for article in articles:
            # Get title
            title = self.get_title(article)

            # Get date
            date = self.get_date(article)

            # Get description, if exists
            description = self.get_description_if_exist(article)

            # Get image name, if exists
            try:
                image = article.find_element('class name', 'css-rq4mmj')
                image_url = image.get_property('src')
                image_url = image_url.split("?")[0]
            except (ElementNotFound, NoSuchElementException):
                image_url = None
                image_name = None
            if image_url is not None:
                image_name = image_url.split("/")[-1]
                i = r.download(image_url, target_file=f"images/{image_name}")

            # Count how many times the query appear in title and description
            count = self.count_query_appearances(title, description)

            # Check if the title or description mentions money
            money_check = self.check_money_appearance(title, description)

            # Put all data into the dictionary
            self.add_to_article_data(
                title,
                date,
                description,
                image_name,
                count,
                money_check
            )

        # Add to excel worksheet
        self.save_article_data_to_workbook()

        self.browser.close_browser()
        return self.article_data
    
    def get_dates(self) -> Tuple[str, str]:
        today = date.today()
        today_date = today.strftime("%Y%m%d")
        today = today - relativedelta(months=self.months_ago)
        start_date = today.strftime("%Y%m%d")
        return start_date, today_date
    
    def get_title(self, article:WebElement) -> str:
        title = article.find_element('class name', 'css-2fgx4k').text
        return title
    
    def get_date(self, article:WebElement) -> str:
        date_element = article.find_element('class name', 'css-17ubb9w')
        date = date_element.text
        return date
    
    def get_description_if_exist(self, article:WebElement) -> Union[str, None]:
        try:
            description = article.find_element('class name', 'css-16nhkrn').text
        except ElementNotFound:
            description = None
        return description
    
    # FUNCTION DOES MORE THAN ONE THING! FIX IT!
    def get_image_name_if_exist(self, article:WebElement) -> Union[str, None]:
        try:
            image = article.find_element('class name', 'css-rq4mmj')
            image_url = image.get_property('src')
            image_url = image_url.split("?")[0]
        except (ElementNotFound, NoSuchElementException):
            image_url = None
            image_name = None
        if image_url is not None:
            image_name = image_url.split("/")[-1]
            self.request.download(image_url, target_file=f"images/{image_name}")
        return image_name
    
    def count_query_appearances(self, title:str, description:Union[str, None]) -> int:
        nrm_query = self.query.lower()
        nrm_title = title.lower()
        count = nrm_title.count(nrm_query)
        if description is not None:
            nrm_description = description.lower()
            count += nrm_description.count(nrm_query)
        return count
    
    def check_money_appearance(self, title:str, description:Union[str, None]) -> bool:
        if description is not None:
            money_check = self.check_money_on_string(title) or self.check_money_on_string(description)
        else:
            money_check = self.check_money_on_string(title)
        return money_check
    
    def add_to_article_data(
            self,
            title:str,
            date:str,
            description:Union[str, None],
            image_name:str,
            query_count:int,
            money_check:bool
    ):
        self.article_data['title'].append(title)
        self.article_data['date'].append(date)
        self.article_data['description'].append(description)
        self.article_data['image'].append(image_name)
        self.article_data['query count'].append(query_count)
        self.article_data['mentions money'].append(money_check)
        print(f"Article Added: {title}")

    @property
    def search(self) -> str:
        section_numbers = f"{self.section_numbers}".replace("[", "|")
        section_numbers = f"{section_numbers}".replace("]", "|")
        return f"{self.query}{section_numbers}{self.months_ago}"
    
    # NEEDS TO BE MORE DYNAMIC, FIX IT!
    def save_article_data_to_workbook(self):
        has_data =  all(self.article_data.values())
        if has_data:
            workbook = self.excel.create_workbook("./article_data.xlsx", sheet_name=self.search)
            self.excel.append_rows_to_worksheet(self.article_data, header=True)
            workbook.save()
        else:
            ValueError("Article data has not been gathered yet")


    def expand_page(self):
        showmore_locator = 'xpath:/html/body/div/div[2]/main/div/div[2]/div[3]/div/button'
        while True:
            try:
                self.browser.click_button(showmore_locator)
            except (ElementNotFound, StaleElementReferenceException):
                break
    
    # OBSOLETE
    def find_and_click_today(self):
        today = str(date.today().day)
        days = self.browser.find_elements('xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div[2]/div/div[3]/div[1]/div[@class="css-hwsp5p "]')
        for day in days:
            if day.text == today:
                day.click()
                break
    
    # OBSOLETE
    def adjust_date(self):
        months_ago = self.months_ago
        # date range
        self.browser.click_button("class:css-p5555t")
        # specific date
        self.browser.click_button("xpath:/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div/ul/li[6]/button")
        # back all month
        for _ in range(months_ago):
            self.browser.click_button("class:css-e0re8i")
        # click today
        self.find_and_click_today()
        # returns to current month
        for _ in range(months_ago):
            self.browser.click_button("class:css-12fzzpb")
        self.find_and_click_today()

        # close date range
        self.browser.click_button("class:css-p5555t")

    def check_money_on_string(self, string:str) -> bool:
        '''check if inside the article exists a pattern that matches probable ways
        of referring to money in dollars, returning a boolean based on that'''
        # for: number + dollar|dollars|USD
        pattern1 = r"\d+(?:\.\d{1,2})?\s(?:dollars?|USD)"
        # for: $ + number
        pattern2 = r"\$\s?\d+"
        match1 = re.search(pattern1, string)
        match2 = re.search(pattern2, string)
        if match1 or match2:
            return True
        else:
            return False

if __name__ == "__main__":
    ig = InfoGetter()
    v = ig.retrieve_info()
    print("data: ", v)