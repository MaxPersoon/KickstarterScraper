import sys
import time
import requests
import pyautogui
from lxml import html
from bs4 import BeautifulSoup


def getResponse(url, session = requests.session(), graphData = None, csrf = None):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"}
    if graphData is None and csrf is None:
        # GET request
        response = session.get(url, headers)
    else:
        # POST request
        headers["x-csrf-token"] = csrf
        response = session.post("https://www.kickstarter.com/graph", json = graphData, headers = headers)

    while response.status_code != 200:
        if response.status_code == 403:
            print("Got locked out. Regaining access...")
            # Open 'Firefox'
            pyautogui.click(275, 1060)
            wait(2)
            # Click on searchbar
            pyautogui.click(350, 60)
            wait(1)
            # Navigate to url
            pyautogui.write(url)
            pyautogui.press('enter')
            wait(2)
            # Do human verification
            pyautogui.mouseDown(250, 350)
            wait(10)
            pyautogui.mouseUp()
            wait(5)
            # Close 'Firefox'
            pyautogui.click(1900, 10)

            if graphData is None and csrf is None:
                # GET request
                response = session.get(url, headers)
            else:
                # POST request
                headers["x-csrf-token"] = csrf
                response = session.post("https://www.kickstarter.com/graph", json=graphData, headers=headers)
        else:
            print("Unable to handle status code", response.status_code)
            sys.exit()

    return session, content

def wait(waitTime):
    startTime = time.time()
    while time.time() - startTime < waitTime:
        continue

def getProjectStory(url):
    # Grab the csrf token
    session, content = getContent(url)
    csrf = content.xpath('//meta[@name="csrf-token"]')[0].get('content')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
        "x-csrf-token": csrf
    }

    # Get the data
    slug = '/'.join(url.split("/")[4:])
    graphData = [{
        "operationName": "Campaign",
        "variables": {
            "slug": slug
        },
        "query": "query Campaign($slug: String!) {\n  project(slug: $slug) {\n    id\n    story\n}\n}\n"
    }]
    response = session.post("https://www.kickstarter.com/graph", json=graphData, headers=headers)

    # Process the data
    data = response.json()
    story = data[0]['data']['project']['story']
    story = BeautifulSoup(story, 'lxml').text
    story = " ".join(story.split())
    print(story)

creatorNameURL = "https://www.kickstarter.com/projects/paperheartsbooks/paper-hearts-bookstore-book-truck/creator_bio"
creatorSerialURL = "https://www.kickstarter.com/profile/paperheartsbooks/created"

urls = ["https://www.kickstarter.com/projects/paperheartsbooks/paper-hearts-bookstore-book-truck"]

for url in urls:
    # Get project's story


    # Get creator's full name

    # Get creator's serial successful entrepreneur status


response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"})
if response.status_code == 403:
    print("403 Forbidden")
    exit()

content = html.fromstring(response.content)
# fullName = content.find_class("identity_name")[0].text.replace("\n", "")
# print(fullName)

# projectCount = int(content.find_class("count")[1].text.replace("\n", ""))
# print(projectCount)
