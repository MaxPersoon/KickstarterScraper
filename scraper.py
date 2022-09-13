import sys
import time
import requests
import pyautogui
from lxml import html
from bs4 import BeautifulSoup


def getData(response):
    # Grab the csrf token
    content = html.fromstring(response.content)
    csrf = content.xpath('//meta[@name="csrf-token"]')[0].get('content')
    headers['x-csrf-token'] = csrf

    # Get the data
    graphData = [{
        "operationName": "Campaign",
        "variables": {
            "slug": 'paperheartsbooks/paper-hearts-bookstore-book-truck'
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


def wait(seconds):
    startTime = time.time()
    while time.time() - startTime < seconds:
        continue


urls = ["https://www.kickstarter.com/projects/paperheartsbooks/paper-hearts-bookstore-book-truck"] * 5

for url in urls:
    dataRetrieved = False

    while not dataRetrieved:
        # Establish a connection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'
        }
        session = requests.session()
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            getData(response)
            dataRetrieved = True
        elif response.status_code == 403:
            print("Got locked out. Regaining access...")
            pyautogui.click(275, 1060)
            wait(2)
            pyautogui.click(350, 60)
            wait(1)
            pyautogui.write(url)
            pyautogui.press('enter')
            wait(2)
            pyautogui.mouseDown(250, 350)
            wait(10)
            pyautogui.mouseUp()
            wait(5)
            pyautogui.click(1900, 10)
        else:
            print("Unable to handle status code", response.status_code)
            sys.exit()
