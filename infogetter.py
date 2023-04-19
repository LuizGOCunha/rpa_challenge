from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.FileSystem import FileSystem

from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary.errors import ElementNotFound
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
)

from datetime import date
from dateutil.relativedelta import relativedelta

from time import sleep

from typing import Union, Tuple, List, Dict, Any

import re

import os

from section import Section
from constants import SECTIONS_DICT

QUERY = os.environ.get("QUERY", "good")

# Adjustment made to make the design more human friendly
SECTION_KEYS = os.environ.get("SECTIONS", ["us", "home"])
SECTIONS = [SECTIONS_DICT[key] for key in SECTION_KEYS]

MONTHS_AGO = os.environ.get("MONTHS_AGO", 1)


class InfoGetter:
    """Class created for the means of facilitating the search, parsing and data storage of a number
    of New York Times articles.
    Initiate the InfoGetter class with its necessary variables, then call the retrieve_info method
    to start the process."""

    browser = Selenium()
    request = HTTP()
    excel = Files()
    fs = FileSystem()
    browser.auto_close = True
    article_data = {
        "title": [],
        "date": [],
        "description": [],
        "image": [],
        "query count": [],
        "mentions money": [],
    }

    def __init__(
        self,
        query: str = QUERY,
        sections: List[str] = SECTIONS,
        months_ago: int = MONTHS_AGO,
    ) -> None:
        self.months_ago = months_ago
        self.sections = sections
        self.query = query

    def retrieve_info(self):
        """Main method of the InfoGetter class. Initiates the process of gathering information
        base on the variables that are given. If no variables are given on class initiation, start search based on
        default values."""
        browser = self.browser
        query = self.query
        start_date, today = self.get_dates()
        url = f"http://www.nytimes.com/search?query={query}&endDate={today}&startDate={start_date}"

        # add sections to url
        url = self.add_sections_to_url(url)

        # open browser
        browser.open_available_browser(url)
        # close ad
        # css selector example: 'css:tagname[attr="attr-value"]'
        browser.click_element('css:button[aria-label="Button to collapse the message"]')

        # click 'see more'
        self.expand_page()

        # get article information from search results
        article_data = self.gather_article_info()

        print("***DONE!***")
        return article_data

    def add_sections_to_url(self, url: str) -> str:
        section_args = "&sections="
        for section in self.sections:
            section_args += section
            section_args += Section.SEP
        section_args = section_args[:-3]
        url += section_args
        return url

    def gather_article_info(self):
        """Gather data from articles if any results are present. Make sure you are in the results page
        when running this function"""
        r = self.request
        results_loc = 'css:ol[data-testid="search-results"]'
        self.browser.page_should_contain_element(
            results_loc, "CurrentPage is not a Results page"
        )
        # The page needs a moment to update the searches
        sleep(1)
        articles = self.browser.find_elements(
            'css:li[data-testid="search-bodega-result"]'
        )
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

            # We check if we have too many files already (Rocoborp cloud has a limit of 50 files)
            if len(self.article_data["title"]) < 47:
                # Put all data into the dictionary
                self.add_to_article_data(
                    title, date, description, image_name, count, money_check
                )
            else:
                print("limit of files achieved")
                break

        # Add to excel worksheet
        self.save_article_data_to_workbook(self.article_data)
        # If its necessary to mandate exactly when to close browser, uncomment below
        # self.browser.close_browser()
        return self.article_data

    def get_dates(self) -> Tuple[str, str]:
        """returns two string dates: one of today and one of an amount of months removed
        from today (months_ago attribute). Returns tuple of start_date and today_date, in
        this exact order."""
        today = date.today()
        today_date = today.strftime("%Y%m%d")
        today = today - relativedelta(months=self.months_ago)
        start_date = today.strftime("%Y%m%d")
        return start_date, today_date

    def get_title(self, article: WebElement) -> str:
        """Receives an article webelement and gets its title element, returning its
        internal text."""
        title = article.find_element("css selector", "div a h4").text
        return title

    def get_date(self, article: WebElement) -> str:
        """Receives an article webelement and gets its date element, returning its
        internal text."""
        date_element = article.find_element(
            "css selector", 'span[data-testid="todays-date"]'
        )
        date = date_element.text
        return date

    def get_description_if_exist(self, article: WebElement) -> Union[str, None]:
        """Receives an article webelement and checks if there is a description element inside,
        returning its internal text. If there is no description webelement, returns None.
        """
        try:
            # We need be as precise as possible, but also need to avoid autogenerated classes
            # Thats why we check for 2 p divs inside link (first: description, second: author)
            p_tags = article.find_elements("css selector", "div a p")
            if len(p_tags) == 1:
                description = None
            else:
                description = p_tags[0].text
        except ElementNotFound:
            description = None
        return description

    def get_image_url_if_exist(self, article: WebElement) -> Tuple[Union[str, None]]:
        """using an article webelement, retrieves url of an image
        returns None if there is no image for the article.
        The returned variables are structured in this manner: (image_url, image_name)"""
        try:
            image = article.find_element("css selector", "figure div img")
            image_src = image.get_property("src")
            image_url = image_src.split("?")[0]
        except (ElementNotFound, NoSuchElementException):
            image_url = None
        return image_url

    def get_image_name(self, image_url: str) -> str:
        """Accepts an image source or url, returns the default image filename present in it.
        If image_url is None, returns None"""
        if image_url is None:
            image_name = None
        else:
            image_name = image_url.split("/")[-1]
        return image_name

    def donwload_image(self, image_url: str, image_name: str):
        """checks if both image_url and image_name are not None, then downloads to the
        following directory: ./output/{image_name}"""
        self.fs.create_directory(os.path.join(".", "output"))
        if image_url and image_name is not None:
            self.request.download(
                image_url, target_file=os.path.join("output", image_name)
            )
            print(f"Image downloaded: {image_name}")

    def count_query_appearances(self, title: str, description: Union[str, None]) -> int:
        """Searches for appearances of query attribute in title and description (if available).
        Not case sensitive."""
        nrm_query = self.query.lower()
        nrm_title = title.lower()
        count = nrm_title.count(nrm_query)
        if description is not None:
            nrm_description = description.lower()
            count += nrm_description.count(nrm_query)
        return count

    def check_money_appearance(self, title: str, description: Union[str, None]) -> bool:
        """Checks if money appears in title and description(if available) using check_money_on_string
        method."""
        if description is not None:
            money_check = self.check_money_on_string(
                title
            ) or self.check_money_on_string(description)
        else:
            money_check = self.check_money_on_string(title)
        return money_check

    def add_to_article_data(
        self,
        title: str,
        date: str,
        description: Union[str, None],
        image_name: str,
        query_count: int,
        money_check: bool,
    ) -> bool:
        """Function that receives all info of an article and appends on all keys of the
        article_data attribute. Returns True if it adds the article info without problem,
        returns False if the article info is a duplicate, not appending it to the data
        """
        # This long statement have the purpose of checking if the gathered data is a duplicate
        # Since the site is unpredictable, i haven't been able to completely prevent duplicates
        # from being gathered, but i can at least prevent them from going into the output
        article_is_duplicate = (
            title in self.article_data["title"]
            and date in self.article_data["date"]
            and description in self.article_data["description"]
            and image_name in self.article_data["image"]
        )
        if article_is_duplicate:
            print(f"Duplicated article: {title}")
            return False
        self.article_data["title"].append(title)
        self.article_data["date"].append(date)
        self.article_data["description"].append(description)
        self.article_data["image"].append(image_name)
        self.article_data["query count"].append(query_count)
        self.article_data["mentions money"].append(money_check)
        print(f"Article Added: {title}")
        return True

    @property
    def search_terms(self) -> str:
        """Property that returns a string that can be used to classify a given search.
        String returns query, sections and months_ago, separated by a "|" character."""
        sections_str = ""
        for section in self.sections:
            section = section.split("%")[0]
            sections_str += section
        return f"{self.query}|{sections_str}|{self.months_ago}"

    def save_article_data_to_workbook(self, data: List[Dict[str, Any]]):
        """Method that can be used to save all data present in the article_data attribute, if
        it has any data in it. Saves it in the a directory called output, using the current date
        as filename, and the search_terms property as sheet name: "./output/{today}.xlsx"
        If document and sheet already exists: resets the sheet inside document.
        If document exists and sheet doesn't: creates a sheet with appropriate name.
        If neither document or sheet exists: creates a document and sheet with appropriate names.
        """
        excel = self.excel
        # Checks if data has been collected
        has_data = all(self.article_data.values())
        filename = date.today().strftime("%Y-%m-%d") + ".xlsx"
        path = os.path.join(".", "output", filename)  # f"./output/{today}.xlsx"
        # Create directory (If exists, proceed without error)
        self.fs.create_directory(os.path.join(".", "output"))  #'./output'
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
                print("File with article data produced successfully.")
        else:
            ValueError("Article data has not been gathered yet")

    def expand_page(self):
        """Method used to identify the "Show more" button inside the results page and click
        it until it expands the page to show all articles. A sleep function of 1 second is used
        inside the loop to prevent the expansion to be too quick, because it can cause article
        duplication."""
        showmore_locator = 'css:[data-testid="search-show-more-button"]'
        while True:
            try:
                # If expansion is too quick it can duplicate articles
                sleep(1)
                self.browser.click_button(showmore_locator)
            except (ElementNotFound, StaleElementReferenceException):
                break

    def check_money_on_string(self, string: str) -> bool:
        """check if inside the article exists a pattern that matches probable ways
        of referring to money in dollars, returning a boolean based on that"""
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
