from RPA.Browser.Selenium import Selenium
from SeleniumLibrary.errors import ElementNotFound
from datetime import date
class InfoGetter:
    browser = Selenium()
    browser.auto_close = False

    def __init__(self, section_numbers:list=[3,6,8], months_ago=1) -> None:
        self.months_ago = months_ago
        browser = self.browser


        browser.open_available_browser("http://www.nytimes.com/search?query=senate")
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

        # self.gather_articles_info()

    
    def get_all_titles(self):
        title_elements = self.browser.find_elements(f'class:css-2fgx4k')
        titles = tuple(map(lambda x: x.text, title_elements))
        return titles

    def expand_page(self):
        showmore_locator = 'xpath:/html/body/div/div[2]/main/div/div[2]/div[3]/div/button'
        while True:
            try:
                self.browser.mouse_up(showmore_locator)
                self.browser.click_button(showmore_locator)
            except ElementNotFound:
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