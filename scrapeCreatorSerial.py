import sys
import time
import requests
import pyautogui
from lxml import html


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
        wait(1)
    else:
        print("Unable to handle status code", statusCode)
        sys.exit()


def wait(waitTime):
    startTime = time.time()
    while time.time() - startTime < waitTime:
        continue


urls = ["https://www.kickstarter.com/profile/skullgarden/created",
        "https://www.kickstarter.com/profile/paperheartsbooks/created"]

session = requests.session()
for url in urls:
    response = session.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) "
                                                       "Gecko/20100101 Firefox/104.0"})

    while response.status_code != 200:
        handleUnwantedStatusCode(response.status_code)
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) "
                                                           "Gecko/20100101 Firefox/104.0"})

    content = html.fromstring(response.content)
    data = content.find_class("project-card-list NS_user__projects_list list ratio-16-9")[0].getchildren()[0].attrib.get('data-projects')
    projects = data.split("},{")
    successfulProjectCounter = 0
    serialEntrepreneur = False
    for project in projects:
        index = project.find("\"state\":\"successful\"")
        if index != -1:
            successfulProjectCounter += 1
            if successfulProjectCounter == 2:
                serialEntrepreneur = True
                break

    if serialEntrepreneur:
        print("Serial entrepreneur")
    else:
        print("Not a serial entrepreneur")

session.close()
