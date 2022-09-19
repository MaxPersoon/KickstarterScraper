import csv
import sys
import time
import requests
import pyautogui
from lxml import html
from bs4 import BeautifulSoup


def loadData(fileName):
    file = open(fileName)
    reader = csv.reader(file)
    next(reader)

    projects_ = []
    for row in reader:
        projects_.append([int(row[0]), row[21], int(row[22])])

    return projects_


def getContent(session_, url_, headers_):
    response_ = session_.get(url_, headers=headers_)

    while response_.status_code != 200:
        if response_.status_code == 403:
            print("403 Forbidden\nRegaining access...")

            # Open 'Firefox' in incognito
            pyautogui.rightClick(275, 1060)
            wait(1)
            pyautogui.leftClick(275, 940)
            wait(1)

            # Click on the address bar
            pyautogui.click(350, 60)
            wait(1)

            # Navigate to url
            pyautogui.write("https://www.kickstarter.com")
            pyautogui.press('enter')
            wait(3)

            # Do human verification
            pyautogui.mouseDown(250, 350)
            wait(10)
            pyautogui.mouseUp()
            wait(5)

            # Close 'Firefox'
            pyautogui.click(1900, 10)
            wait(1)
        else:
            print("Unable to handle status code", response_.status_code)
            sys.exit()

        response_ = session_.get(url_, headers=headers_)

    return html.fromstring(response_.content)


def wait(waitTime):
    startTime = time.time()
    while time.time() - startTime < waitTime:
        continue


projects = loadData('input.csv')

session = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"}
csrf = getContent(session, "https://www.kickstarter.com", headers).xpath('//meta[@name="csrf-token"]')[0].get('content')
headers["x-csrf-token"] = csrf

for project in projects:
    # Get creator's full name
    url = "https://www.kickstarter.com/projects/" + project[1] + "/creator_bio"
    fullName = getContent(session, url, headers).find_class("identity_name")[0].text.replace("\n", "")
    output = "Name: " + fullName

    # Get creator's serial successful entrepreneurship status
    url = "https://www.kickstarter.com/profile/" + project[1].split("/")[0] + "/created"
    data = getContent(session, url, headers).find_class("project-card-list NS_user__projects_list list ratio-16-9")[0].getchildren()[0].attrib.get('data-projects')
    creatorProjects = data.split("},{")
    successfulProjectCounter = 0
    for creatorProject in creatorProjects:
        deadlineIndex = creatorProject.find("\"deadline\":")
        deadline = int(creatorProject[deadlineIndex + 11:deadlineIndex + 21])
        if deadline < project[2]:
            successfulIndex = creatorProject.find("\"state\":\"successful\"")
            if successfulIndex != -1:
                successfulProjectCounter += 1
                if successfulProjectCounter == 2:
                    output += "; Serial: 1"
                    break

    if successfulProjectCounter < 2:
        output += "; Serial: 0"

    # Get project's story
    graphData = [{
        "operationName": "Campaign",
        "variables": {
            "slug": project[1]
        },
        "query": "query Campaign($slug: String!) {\n  project(slug: $slug) {\n    id\n    story\n}\n}\n"
    }]
    response = session.post("https://www.kickstarter.com/graph", json=graphData, headers=headers)

    while response.status_code != 200:
        if response.status_code == 429:
            print("429 Too Many Requests\nWaiting for 300 seconds...")
            wait(300)
            response = session.post("https://www.kickstarter.com/graph", json=graphData, headers=headers)
        else:
            print("Unable to handle status code", response.status_code)
            sys.exit()

    data = response.json()
    story = data[0]['data']['project']['story']
    story = BeautifulSoup(story, 'lxml').text
    story = " ".join(story.split())
    output += "; Story: " + story

    print(output)
    wait(5)

session.close()
