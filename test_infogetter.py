import pytest
import validators
from selenium.common.exceptions import NoSuchElementException
from datetime import date
from dateutil import relativedelta


from infogetter import InfoGetter
from constants import SECTION_XPATH_DICT, LINK_LIST_EXAMPLE, LINK_LIST_POSTPROCESS

class TestInfoGetter:

    @pytest.mark.skip(reason="Takes too long, only test it from time to time")
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

    
    

