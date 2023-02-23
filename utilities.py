import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
global NYT
NYT = "https://www.nytimes.com"

from constants import SECTION_XPATH_DICT

SECTION_XPATH_DICT = {

}

# Necessary variables
query = "senate"
section = "new york"

def get_html_from_query(query, section):
    driver = webdriver.Firefox()
    driver.get(f"https://www.nytimes.com/search?query={query}")
    section = driver.find_element(By.XPATH, value="/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/button/label")
    section.click()
    sleep(0.5)
    section = driver.find_element(By.XPATH, value=SECTION_XPATH_DICT[section]) 
    section.click()
    sleep(0.5)
    html = driver.page_source
    driver.close()

    bs = BeautifulSoup(html, features="lxml")
    html_p = bs.prettify()
    return html_p
get_html_from_query(query,section)
print("done!")

def return_html_from_url(url):
    r = requests.get(f'{url}')
    return r.text

# Find each article
# Check the date of the articles
def return_list_of_lastest_articles(query):
    html = get_html_from_query(f"{query}")
    soup = BeautifulSoup(html, features="lxml")
    anchors = soup.find_all("a")
    links_list = []
    for tag in anchors:
        if tag.has_attr("href"):
            link = tag.attrs["href"]
            has_date_length = len(link) > 10
            from_current_year = link[0:6] == "/2023/"
            if has_date_length and from_current_year:
                link = tag.attrs["href"]
                links_list.append(link)
    article_list = []
    for link in links_list:
        article = NYT + link  
        article_list.append(article)
    return article_list

def return_article_headline(url):
    driver = webdriver.Firefox()
    driver.get(url)
    article_html = driver.page_source
    driver.close()

    soup = BeautifulSoup(article_html, features="lxml")
    h1s = soup.find_all("h1")
    for tag in h1s:
        if tag.has_attr("data-testid"):
            if tag.attrs["data-testid"] == "headline":
                headline = tag.getText()

    return headline


article_list = return_list_of_lastest_articles("senate")

driver = webdriver.Firefox()
for article in article_list:
    driver.get(article)

    

    driver.close()
    breakpoint()