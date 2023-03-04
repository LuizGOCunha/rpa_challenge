NYT = "https://www.nytimes.com"

# OBSOLETE
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

# OBSOLETE
SECTION_XPATH_LIST = list(SECTION_XPATH_DICT.values())

# OBSOLETE
LINK_LIST_EXAMPLE = ['https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1', 
'https://www.nytimes.com/2023/02/15/us/politics/california-senator-feinstein-retire.html?searchResultPosition=2', 'https://www.nytimes.com/2023/02/10/us/politics/john-fetterman-senate-stroke.html?searchResultPosition=3', 
'https://www.nytimes.com/2023/02/23/opinion/dianne-feinstein-retirement.html?searchResultPosition=5', 'https://www.nytimes.com/2023/02/17/us/politics/fetterman-mental-illness-stigma.html?searchResultPosition=6', 
'https://www.nytimes.com/2020/02/17/us/politics/rick-scott-social-security.html?searchResultPosition=7', 'https://www.nytimes.com/2020/02/16/us/politics/john-fetterman-health.html?searchResultPosition=8', 
'https://www.nytimes.com/2020/02/16/us/politics/rick-scott-social-security.html?searchResultPosition=9', 'https://www.nytimes.com/2020/02/15/us/politics/biden-documents-university-delaware.html?searchResultPosition=10']

# OBSOLETE
LINK_LIST_POSTPROCESS = ['https://www.nytimes.com/2023/02/21/us/politics/barbara-lee-senate-california.html?searchResultPosition=1', 
'https://www.nytimes.com/2023/02/15/us/politics/california-senator-feinstein-retire.html?searchResultPosition=2', 'https://www.nytimes.com/2023/02/10/us/politics/john-fetterman-senate-stroke.html?searchResultPosition=3', 
'https://www.nytimes.com/2023/02/23/opinion/dianne-feinstein-retirement.html?searchResultPosition=5', 'https://www.nytimes.com/2023/02/17/us/politics/fetterman-mental-illness-stigma.html?searchResultPosition=6']

SECTIONS_DICT = {
    'arts': 'Arts%7Cnyt%3A%2F%2Fsection%2F6e6ee292-b4bd-5006-a619-9ceab03524f2',
    'books': 'Books%7Cnyt%3A%2F%2Fsection%2F550f75e2-fc37-5d5c-9dd1-c665ac221b49',
    'business': 'Business%7Cnyt%3A%2F%2Fsection%2F0415b2b0-513a-5e78-80da-21ab770cb753',
    'movies': 'Movies%7Cnyt%3A%2F%2Fsection%2F62b3d471-4ae5-5ac2-836f-cb7ad531c4cb',
    'new york': 'New%20York%7Cnyt%3A%2F%2Fsection%2F39480374-66d3-5603-9ce1-58cfa12988e2',
    'opinion': 'Opinion%7Cnyt%3A%2F%2Fsection%2Fd7a71185-aa60-5635-bce0-5fab76c7c297',
    'sports': 'Sports%7Cnyt%3A%2F%2Fsection%2F4381411b-670f-5459-8277-b181485a19ec',
    'style': 'Style%7Cnyt%3A%2F%2Fsection%2F146e2c45-6586-59ef-bc23-90e88fe2cf0a',
    'us': 'U.S.%7Cnyt%3A%2F%2Fsection%2Fa34d3d6c-c77f-5931-b951-241b4e28681c',
    'world': 'World%7Cnyt%3A%2F%2Fsection%2F70e865b6-cc70-5181-84c9-8368b3a5c34b',
    'wir': 'Week%20in%20Review%7Cnyt%3A%2F%2Fsection%2F33252b7a-ff01-5531-8830-cd6afa997b6e',
    'travel': 'Travel%7Cnyt%3A%2F%2Fsection%2Fb2fb7c08-4f8e-5cff-8e14-aff8a49a9934',
    'home': 'Home%7Cnyt%3A%2F%2Fsection%2Fd7a71185-aa60-5635-bce0-5fab76c7c29'
}
SEPARATOR = '%2C'