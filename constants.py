NYT = "https://www.nytimes.com"

# Obsolete
SECTION_XPATH_DICT = {
    'blogs': '/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[2]/label/input',
    'briefing': '/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[3]/label/input',
    'business': '/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[4]/label/input',
    'new york': '/html/body/div/div[2]/main/div/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[5]/label/input',
    'opinion': '/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[6]/label/input',
    'us': '/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[7]/label/input',
    'washington': '/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[8]/label/input',
    'week in review': '/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[9]/label/input',
    'world': '/html/body/div/div[2]/main/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/ul/li[10]/label/input'
}

SECTION_XPATH_LIST = list(SECTION_XPATH_DICT.values())

LINK_LIST_EXAMPLE = ['https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1', 
'https://www.nytimes.com/2023/02/15/us/politics/california-senator-feinstein-retire.html?searchResultPosition=2', 'https://www.nytimes.com/2023/02/10/us/politics/john-fetterman-senate-stroke.html?searchResultPosition=3', 
'https://www.nytimes.com/2023/02/23/opinion/dianne-feinstein-retirement.html?searchResultPosition=5', 'https://www.nytimes.com/2023/02/17/us/politics/fetterman-mental-illness-stigma.html?searchResultPosition=6', 
'https://www.nytimes.com/2020/02/17/us/politics/rick-scott-social-security.html?searchResultPosition=7', 'https://www.nytimes.com/2020/02/16/us/politics/john-fetterman-health.html?searchResultPosition=8', 
'https://www.nytimes.com/2020/02/16/us/politics/rick-scott-social-security.html?searchResultPosition=9', 'https://www.nytimes.com/2020/02/15/us/politics/biden-documents-university-delaware.html?searchResultPosition=10']

LINK_LIST_POSTPROCESS = ['https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1', 
'https://www.nytimes.com/2023/02/15/us/politics/california-senator-feinstein-retire.html?searchResultPosition=2', 'https://www.nytimes.com/2023/02/10/us/politics/john-fetterman-senate-stroke.html?searchResultPosition=3', 
'https://www.nytimes.com/2023/02/23/opinion/dianne-feinstein-retirement.html?searchResultPosition=5', 'https://www.nytimes.com/2023/02/17/us/politics/fetterman-mental-illness-stigma.html?searchResultPosition=6']