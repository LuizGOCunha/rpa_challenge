import pytest
import validators
from selenium.common.exceptions import NoSuchElementException
from datetime import date
from dateutil import relativedelta


from infogetter import InfoGetter
from constants import SECTION_XPATH_DICT, LINK_LIST_EXAMPLE, LINK_LIST_POSTPROCESS

class TestInfoGetter:
    link = 'https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1'
    with open("html_article_example.txt", "r") as file:
        article_html = file.read()

    #@pytest.mark.skip(reason="Takes too long, only test it from time to time")
    def test_if_we_can_get_search_html_from_all_sections(self):
        sectionsdict = SECTION_XPATH_DICT
        for section in sectionsdict.keys():
            ig = InfoGetter("senate", section, 1)
            try:
                html = ig.get_query_html()
                assert html, f"Section {section} returns empty element"
            except NoSuchElementException:
                assert False, f"Section {section} element not found."
    

    def test_if_we_can_detect_a_date(self):
        date = "/2023/10/10/"
        not_date1 = "lskdalkjfefuj"
        not_date2 = "2025684214"
        not_date3 = "/1/1/1/2/3/4"
        ig = InfoGetter()
        assert ig.is_date(date)
        assert not ig.is_date(not_date1)
        assert not ig.is_date(not_date2)
        assert not ig.is_date(not_date3)
        

    def test_if_we_can_parse_links_from_html_query(self):
        with open("html_query_example.txt", "r") as file:
            html_query = file.read()
        ig = InfoGetter()
        ig.html_query = html_query
        list_of_articles = ig.get_list_of_articles_urls()
        print(list_of_articles)
        assert list_of_articles
        for article_link in list_of_articles:
            assert validators.url(article_link), f"string is not a link: {article_link}"

    def test_if_we_can_check_if_date_is_appropriate(self):
        ig = InfoGetter(months = 120)
        date1 = date(2020, 10, 9)
        date2 = date(2017, 1, 12)
        date3 = date(1900, 4, 15)
        assert ig.check_if_date_is_appropriate(date1)
        assert ig.check_if_date_is_appropriate(date2)
        assert not ig.check_if_date_is_appropriate(date3)
    
    def test_if_we_can_get_date_from_article_link(self):
        link = 'https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1'
        ig = InfoGetter()
        article_date = ig.get_date_from_link(link)
        assert article_date == date(2023, 2, 21)

    def test_if_we_can_appropriately_filter_a_link_list(self):
        ig = InfoGetter(months = 12)
        ig.article_list = LINK_LIST_EXAMPLE
        ig.filter_article_links()
        assert ig.article_list == LINK_LIST_POSTPROCESS

    def test_if_we_can_get_html_from_url(self):
        ig = InfoGetter()
        html = ig.get_html_from_url(self.link)
        assert html

    def test_if_we_can_get_title_from_html(self):
        ig = InfoGetter()
        title = ig.get_title_from_html(self.article_html)
        assert title == "Barbara Lee, a Longtime Congresswoman, Is Running for Senate in California"
    
    def test_if_we_can_get_description_from_html(self):
        ig = InfoGetter()
        description = ig.get_description_from_html(self.article_html)
        assert description == "Ms. Lee, the sole member of Congress to oppose a broad war authorization after the Sept. 11 attacks, is joining the race for Senator Dianne Feinstein’s seat."

    def test_if_we_can_get_image_link_from_html(self):
        ig = InfoGetter()
        image_link = ig.get_image_link_from_html(self.article_html)
        assert validators.url(image_link)
        assert image_link == "https://static01.nyt.com/images/2023/01/13/multimedia/13pol-barbara-lee-photo-whkz/13pol-barbara-lee-photo-whkz-articleLarge.jpg?quality=75&auto=webp&disable=upscale"
    
    def test_if_we_can_recognize_money_on_strings(self):
        ig = InfoGetter()
        string1 = "$123"
        string2 = "$ 345"
        string3 = "$ 123 assdfd"
        string4 = "123 dollars"
        string5 = "333 USDss"
        string6 = "1 dollarwessa"
        string7 = "asdasdwessa"
        string8 = "$ sessa"
        assert ig.check_money_on_html(string1)
        assert ig.check_money_on_html(string2)
        assert ig.check_money_on_html(string3)
        assert ig.check_money_on_html(string4)
        assert ig.check_money_on_html(string5)
        assert ig.check_money_on_html(string6)
        assert not ig.check_money_on_html(string7)
        assert not ig.check_money_on_html(string8)

    def test_if_we_can_get_appropriate_info(self):
        expected_info = {
            "url": self.link,
            "title": "Barbara Lee, a Longtime Congresswoman, Is Running for Senate in California",
            "date": "2023-02-21",
            "description": "Ms. Lee, the sole member of Congress to oppose a broad war authorization after the Sept. 11 attacks, is joining the race for Senator Dianne Feinstein’s seat.",
            "picture filename": "https://static01.nyt.com/images/2023/01/13/multimedia/13pol-barbara-lee-photo-whkz/13pol-barbara-lee-photo-whkz-articleLarge.jpg?quality=75&auto=webp&disable=upscale",
            "search appearances": 29,
            "mentions money": True
        }
        ig = InfoGetter()
        
        info = ig.get_article_info_from_url(self.link)
        assert info == expected_info
    

