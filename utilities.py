import requests
from bs4 import BeautifulSoup
from selenium import webdriver

driver = webdriver.Firefox()
driver.get("https://www.nytimes.com")

driver.close()

def return_html_from_query(query):
    r = requests.get(f'https://www.nytimes.com/search?query={query}')
    return r.text
