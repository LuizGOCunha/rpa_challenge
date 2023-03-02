from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from selenium.webdriver.remote.webdriver import WebDriver
from SeleniumLibrary.errors import ElementNotFound
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from datetime import date



class InfoGetter:
    browser = Selenium()
    request = HTTP()
    browser.auto_close = False
    article_data = None

    def __init__(self, query="senate",section_numbers:list=[3,6,8], months_ago=1) -> None:
        self.months_ago = months_ago
        self.section_numbers = section_numbers
        self.query = query

    def retrieve_info(self):
        browser = self.browser
        section_numbers = self.section_numbers
        query = self.query
        r = self.request


        browser.open_available_browser(f"http://www.nytimes.com/search?query={query}")
        # close ad
        browser.click_element('xpath://*[@id="site-content"]/div[2]/div[1]/div/div[2]/button')
        # click section dropdown
        browser.click_element("xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/button")
        # click sections
        for sn in section_numbers:
            try:
                browser.click_element(f"xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[{sn}]/label/input")
            except ElementNotFound:
                raise ValueError("Section number does not exist")

        

        articles = browser.find_elements('//html/body/div/div[2]/main/div[1]/div[2]/div[2]/ol/li[@data-testid="search-bodega-result"]')
        i = 1

        self.adjust_date()

        self.expand_page()

        # gather info from articles
        articles = self.browser.find_elements('class:css-1l4w6pd')
        for article in articles:
            # Get title
            title = article.find_element('class name', 'css-2fgx4k').text
            print("title: ", title)

            # Get description, if exists
            try:
                description = article.find_element('class name', 'css-16nhkrn').text
            except ElementNotFound:
                description = None
            print("description: ", description)

            # Get image name, if exists
            try:
                image = article.find_element('class name', 'css-rq4mmj')
                image_url = image.get_property('src')
                image_url = image_url.split("?")[0]
            except (ElementNotFound, NoSuchElementException):
                image_url = None
            if image_url is not None:
                image_name = image_url.split("/")[-1]
                i = r.download(image_url, target_file=f"images/{image_name}")
                print("image name: ", image_name)

            # Count how many times the query appear in title and description
            nrm_query = self.query.lower()
            nrm_title = title.lower()
            count = nrm_title.count(nrm_query)
            if description is not None:
                nrm_description = description.lower()
                count += nrm_description.count(nrm_query)
            print("count: ", count)

            # Put all data into one dictionary
            if self.article_data is None:
                self.article_data = []
            self.article_data.append({
                'title': title,
                'description': description,
                'image': image_name,
                'query count': count,
                # mentions money: bool
            })
        print(self.article_data)
        breakpoint()



    def expand_page(self):
        showmore_locator = 'xpath:/html/body/div/div[2]/main/div/div[2]/div[3]/div/button'
        while True:
            try:
                self.browser.mouse_over(showmore_locator)
                self.browser.click_button(showmore_locator)
            except (ElementNotFound, StaleElementReferenceException):
                break

    def find_and_click_today(self):
        today = str(date.today().day)
        days = self.browser.find_elements('xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div[2]/div/div[3]/div[1]/div[@class="css-hwsp5p "]')
        for day in days:
            if day.text == today:
                day.click()
                break
        
    def adjust_date(self):
        months_ago = self.months_ago
        # date range
        self.browser.click_button("xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/button")
        # specific date
        self.browser.click_button("xpath:/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[1]/div/div/div/ul/li[6]/button")
        # back all month
        for _ in range(months_ago):
            self.browser.click_button("xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div[1]/button[1]")
        # click today
        self.find_and_click_today()
        # returns to current month
        for _ in range(months_ago):
            self.browser.click_button("xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div/div[1]/button[2]")
        self.find_and_click_today()

        # close date range
        self.browser.click_button("xpath:/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[1]/div/div/button")

ig = InfoGetter()
ig.retrieve_info()