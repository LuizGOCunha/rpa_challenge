from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.FileSystem import FileSystem

from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary.errors import ElementNotFound
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from datetime import date
from dateutil.relativedelta import relativedelta

from time import sleep

from typing import Union, Tuple, List, Dict, Any

import re

from section import Section


class InfoGetter:
    '''Class created for the means of facilitating the search, parsing and data storage of a number
    of New York Times articles.
    Initiate the InfoGetter class with its necessary variables, then call the retrieve_info method
    to start the process.'''
    browser = Selenium()
    request = HTTP()
    excel = Files()
    fs = FileSystem()
    browser.auto_close = True
    article_data = {
                'title': [],
                'date': [],
                'description': [],
                'image': [],
                'query count': [],
                'mentions money': []
            }

    def __init__(self, query:str="usa",sections:List[Section]=[Section.ARTS,Section.TRAVEL], months_ago:int=1) -> None:
        self.months_ago = months_ago
        self.sections = sections
        self.query = query

    def retrieve_info(self):
        '''Main method of the InfoGetter class. Initiates the process of gathering information
        base on the variables that are given. If no variables are given on class initiation, start search based on
        default values.'''
        browser = self.browser
        query = self.query
        start_date, today = self.get_dates()
        url = f"http://www.nytimes.com/search?query={query}&endDate={today}&startDate={start_date}"

        # add sections to url
        url = self.add_sections_to_url(url)

        # open browser
        browser.open_available_browser(url)

        # close ad
        browser.click_element('class:css-1qw5f1g')

        # click 'see more'
        self.expand_page()

        # get article information from search results
        article_data = self.gather_article_info()

        return article_data
    
    def add_sections_to_url(self, url:str) -> str:
        section_args = '&sections='
        for section in self.sections:
            section_args += section
            section_args += Section.SEP
        section_args = section_args[:-3]
        url += section_args
        return url
        
    def gather_article_info(self):
        '''Gather data from articles if any results are present. Make sure you are in the results page
        when running this function'''
        r = self.request
        results_div_id = "class:css-46b038"
        self.browser.page_should_contain_element(results_div_id, "CurrentPage is not a Results page")
        # The page needs a moment to update the searches
        sleep(1)
        articles = self.browser.find_elements('class:css-1l4w6pd')
        if not articles:
            raise ValueError("Your search returned no results")

        for article in articles:
            # Get title
            title = self.get_title(article)

            # Get date
            date = self.get_date(article)

            # Get description, if exists
            description = self.get_description_if_exist(article)

            # Get image name and url, if exists, then download it
            image_url = self.get_image_url_if_exist(article)
            image_name = self.get_image_name(image_url)
            self.donwload_image(image_url, image_name)

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
        self.save_article_data_to_workbook(self.article_data)
        # If its necessary to mandate exactly when to close browser, uncomment below
        # self.browser.close_browser()
        return self.article_data
    
    def get_dates(self) -> Tuple[str, str]:
        '''returns two string dates: one of today and one of an amount of months removed
        from today (months_ago attribute). Returns tuple of start_date and today_date, in 
        this exact order.'''
        today = date.today()
        today_date = today.strftime("%Y%m%d")
        today = today - relativedelta(months=self.months_ago)
        start_date = today.strftime("%Y%m%d")
        return start_date, today_date
    
    def get_title(self, article:WebElement) -> str:
        '''Receives an article webelement and gets its title element, returning its
        internal text.'''
        title = article.find_element('class name', 'css-2fgx4k').text
        return title
    
    def get_date(self, article:WebElement) -> str:
        '''Receives an article webelement and gets its date element, returning its
        internal text.'''
        date_element = article.find_element('class name', 'css-17ubb9w')
        date = date_element.text
        return date
    
    def get_description_if_exist(self, article:WebElement) -> Union[str, None]:
        '''Receives an article webelement and checks if there is a description element inside,
        returning its internal text. If there is no description webelement, returns None.'''
        try:
            description = article.find_element('class name', 'css-16nhkrn').text
        except ElementNotFound:
            description = None
        return description
    
    
    def get_image_url_if_exist(self, article:WebElement) -> Tuple[Union[str, None]]:
        '''using an article webelement, retrieves url of an image
        returns None if there is no image for the article. 
        The returned variables are structured in this manner: (image_url, image_name)'''
        try:
            image = article.find_element('class name', 'css-rq4mmj')
            image_src = image.get_property('src')
            image_url = image_src.split("?")[0]
        except (ElementNotFound, NoSuchElementException):
            image_url = None
        return image_url
    
    def get_image_name(self, image_url:str) -> str:
        '''Accepts an image source or url, returns the default image filename present in it.
        If image_url is None, returns None'''
        if image_url is None:
            image_name = None
        else:
            image_name = image_url.split("/")[-1]
        return image_name

    def donwload_image(self, image_url:str, image_name:str):
        '''checks if both image_url and image_name are not None, then downloads to the 
        following directory: ./images/{image_name}'''
        self.fs.create_directory("./images")
        if image_url and image_name is not None:
            self.request.download(image_url, target_file=f"images/{image_name}")
    
    def count_query_appearances(self, title:str, description:Union[str, None]) -> int:
        '''Searches for appearances of query attribute in title and description (if available).
        Not case sensitive.'''
        nrm_query = self.query.lower()
        nrm_title = title.lower()
        count = nrm_title.count(nrm_query)
        if description is not None:
            nrm_description = description.lower()
            count += nrm_description.count(nrm_query)
        return count
    
    def check_money_appearance(self, title:str, description:Union[str, None]) -> bool:
        '''Checks if money appears in title and description(if available) using check_money_on_string
        method.'''
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
        '''Function that receives all info of an article and appends on all keys of the 
        article_data attribute.'''
        self.article_data['title'].append(title)
        self.article_data['date'].append(date)
        self.article_data['description'].append(description)
        self.article_data['image'].append(image_name)
        self.article_data['query count'].append(query_count)
        self.article_data['mentions money'].append(money_check)
        print(f"Article Added: {title}")

    @property
    def search_terms(self) -> str:
        '''Property that returns a string that can be used to classify a given search.
        String returns query, sections and months_ago, separated by a "|" character.'''
        sections_str = ''
        for section in self.sections:
            section = section.split('%')[0]
            sections_str += section
        return f"{self.query}|{sections_str}|{self.months_ago}"

    def save_article_data_to_workbook(self, data:List[Dict[str, Any]]):
        '''Method that can be used to save all data present in the article_data attribute, if
        it has any data in it. Saves it in the a directory called data, using the current date 
        as filename, and the search_terms property as sheet name: "./data/{today}.xlsx"
        If document and sheet already exists: resets the sheet inside document.
        If document exists and sheet doesn't: creates a sheet with appropriate name.
        If neither document or sheet exists: creates a document and sheet with appropriate names.'''
        excel = self.excel
        has_data =  all(self.article_data.values())
        today = date.today().strftime('%Y-%m-%d')
        path = f"./data/{today}.xlsx"
        # Create directory (If exists, proceed without error)
        self.fs.create_directory('./data')
        title = self.search_terms
        if has_data:
            try:
                # Case of WB exists and WS exists
                workbook = excel.open_workbook(path)
                # Reset worksheet
                excel.remove_worksheet(title)
                excel.create_worksheet(title)
            except FileNotFoundError:
                # Case of WB not existing
                workbook = excel.create_workbook(path, sheet_name=title)
            except (ValueError, KeyError):
                # Case of WS not existing
                workbook = excel.open_workbook(path)
                workbook.create_worksheet(title)
            finally:
                excel.append_rows_to_worksheet(data, header=True)
                workbook.save()
                workbook.close()
        else:
            ValueError("Article data has not been gathered yet")


    def expand_page(self):
        '''Method used to identify the "Show more" button inside the results page and click
        it until it expands the page to show all articles. A sleep function of 1 second is used
        inside the loop to prevent the expansion to be too quick, because it can cause article 
        duplication.'''
        showmore_locator = 'css:[data-testid="search-show-more-button"]'
        while True:
            
            try:
                # If expansion is too quick it can duplicate articles
                sleep(1)
                self.browser.click_button(showmore_locator)  
            except (ElementNotFound, StaleElementReferenceException):
                break
    
    # OBSOLETE
    def find_and_click_today(self):
        '''***OBSOLETE!***
        Suport method used in the adjust_date method to find the appropriate day in the calendar element'''
        today = str(date.today().day)
        days = self.browser.find_elements('xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div[2]/div/div[3]/div[1]/div[@class="css-hwsp5p "]')
        for day in days:
            if day.text == today:
                day.click()
                break
    
    # OBSOLETE
    def adjust_date(self):
        '''***OBSOLETE!***
        A method that is used to manually adjust the date in our search page.
        Made obsolete after figuring out that making that adjustment in the url is quicker
        and easier.'''
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