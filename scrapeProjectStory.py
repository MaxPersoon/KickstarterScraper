import sys
import time
import requests
import pyautogui
from lxml import html
from bs4 import BeautifulSoup


def handleUnwantedStatusCode(statusCode):
    if statusCode == 403:
        print("Got locked out. Regaining access...")
        # Open 'Firefox'
        pyautogui.rightClick(275, 1060)
        wait(1)
        pyautogui.leftClick(275, 940)
        wait(1)
        # Click on searchbar
        pyautogui.click(350, 60)
        wait(1)
        # Navigate to url
        pyautogui.write(url)
        pyautogui.press('enter')
        wait(3)
        # Do human verification
        pyautogui.mouseDown(250, 350)
        wait(10)
        pyautogui.mouseUp()
        wait(5)
        # Close 'Firefox'
        pyautogui.click(1900, 10)
    else:
        print("Unable to handle status code", statusCode)
        sys.exit()


def wait(waitTime):
    startTime = time.time()
    while time.time() - startTime < waitTime:
        continue


session = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"}
response = session.get("https://www.kickstarter.com/", headers=headers)
csrf = html.fromstring(response.content).xpath('//meta[@name="csrf-token"]')[0].get('content')
headers["x-csrf-token"] = csrf

url = "https://www.kickstarter.com/projects/paperheartsbooks/paper-hearts-bookstore-book-truck"
startTime = time.time()
while time.time() - startTime < 180:
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

    if response.status_code == 403:
        print("403 Forbidden")
        break

    # Process the data
    try:
        data = response.json()
        story = data[0]['data']['project']['story']
        story = BeautifulSoup(story, 'lxml').text
        story = " ".join(story.split())
        print(story)
    except json.decoder.JSONDecodeError:
        print("JSON error")

    # response = session.get(url, headers=headers)
    #
    # if response.status_code == 403:
    #     print("403 Forbidden")
    #     break
    #
    # content = html.fromstring(response.content)
    # fullName = content.find_class("identity_name")[0].text.replace("\n", "")
    # print(fullName)

    wait(1)

session.close()
