import vlc
import sys
import csv
import time
import requests
from lxml import html
from bs4 import BeautifulSoup


def loadData():
    dataReader = csv.reader(open('Scraped Data\\data.csv', encoding='cp1252'))
    skippedReader = open('Scraped Data\\skipped.txt', encoding='cp1252')
    next(dataReader)

    projectIDsToRemove = []
    for row in dataReader:
        projectIDsToRemove.append(int(row[0]))
    for line in skippedReader:
        projectIDsToRemove.append(int(line.strip()))

    del dataReader
    skippedReader.close()

    inputReader = csv.reader(open('input.csv', encoding='cp1252'))
    next(inputReader)

    projects_ = []
    for row in inputReader:
        projectID = int(row[0])
        if projectID in projectIDsToRemove:
            continue
        projects_.append([projectID, int(row[1]), float(row[2]), float(row[3]), int(row[4]), float(row[5]), int(row[6]),
                          int(row[7]), int(row[8]), int(row[9]), int(row[10]), int(row[11]), int(row[12]), int(row[13]),
                          int(row[14]), int(row[15]), int(row[16]), int(row[17]), int(row[18]), int(row[19]), int(row[20]),
                          int(row[21]), int(row[22]), row[23], int(row[24])])

    del inputReader

    return projects_


def getOKResponse(url_, graphData_):
    if graphData_ is None:
        response_ = session.get(url_, headers=headers)
    else:
        response_ = session.post(url_, headers=headers, json=graphData_)

    while response_.status_code != 200:
        print("Status code: " + str(response_.status_code))
        if response_.status_code == 403:
            vlc.MediaPlayer('hangover-sound.mp3').play()
            print("Waiting to continue...")
            input()
            print("Continuing...")
        elif response_.status_code == 429:
            print("Waiting for 300 seconds...")
            wait(300)
        else:
            print("Exiting...")
            sys.exit()

        if graphData_ is None:
            response_ = session.get(url_, headers=headers)
        else:
            response_ = session.post(url_, headers=headers, json=graphData_)

    return response_


def wait(waitTime):
    startTime = time.time()
    while time.time() - startTime < waitTime:
        continue


delay = 5
projects = loadData()
dataWriter = csv.writer(open('Scraped Data\\data.csv', 'a', newline='', encoding='cp1252'))
skippedWriter = open('Scraped Data\\skipped.txt', 'a', encoding='cp1252')

session = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0"}
csrf = html.fromstring(getOKResponse("https://www.kickstarter.com/", None).content).xpath('//meta[@name="csrf-token"]')[0].get('content')
headers["x-csrf-token"] = csrf

cntr = 0
for project in projects[:1000]:
    cntr += 1
    wait(delay)

    # Get proper slug
    url = "https://www.kickstarter.com/projects/" + project[23]
    response = getOKResponse(url, None)
    if "View copyright notification" in response.text:
        print(str(cntr) + "/" + str(len(projects)) + ": " + "skipped (DMCA strike)")
        skippedWriter.write(str(project[0]) + "\n")
        continue
    if "has been hidden for privacy" in response.text:
        print(str(cntr) + "/" + str(len(projects)) + ": " + "skipped (hidden)")
        skippedWriter.write(str(project[0]) + "\n")
        continue
    if "intellectual property dispute" in response.text:
        print(str(cntr) + "/" + str(len(projects)) + ": " + "skipped (IP dispute)")
        skippedWriter.write(str(project[0]) + "\n")
        continue
    if response.url != url:
        project[23] = '/'.join(response.url.split("/")[4:6])
    videoPitch = len(html.fromstring(response.content).xpath("//*[@id='video_pitch']")) > 0

    # Get variable 'creator_name'
    url = "https://www.kickstarter.com/projects/" + project[23] + "/creator_bio"
    fullName = html.fromstring(getOKResponse(url, None).content).find_class("identity_name")[0].text.replace("\n", "")
    fullName = fullName.encode('cp1252', 'ignore').decode('cp1252')
    if fullName == "(name not available)":
        print(str(cntr) + "/" + str(len(projects)) + ": " + "skipped (hidden name)")
        skippedWriter.write(str(project[0]) + "\n")
        continue
    project.append(fullName)

    # Get variable 'serial_entrepreneur'
    url = "https://www.kickstarter.com/profile/" + project[23].split("/")[0] + "/created"
    data = html.fromstring(getOKResponse(url, None).content).find_class("project-card-list NS_user__projects_list list ratio-16-9")
    if len(data) == 0:
        print(str(cntr) + "/" + str(len(projects)) + ": " + "skipped (deleted profile)")
        skippedWriter.write(str(project[0]) + "\n")
        continue
    data = data[0].getchildren()[0].attrib.get('data-projects')

    creatorProjects = data.split("},{")
    successfulProjectCounter = 0
    for creatorProject in creatorProjects:
        deadlineIndex = creatorProject.find("\"deadline\":")
        deadline = int(creatorProject[deadlineIndex + 11:deadlineIndex + 21])
        if deadline < project[24]:
            successfulIndex = creatorProject.find("\"state\":\"successful\"")
            if successfulIndex != -1:
                successfulProjectCounter += 1
                if successfulProjectCounter == 2:
                    project.append(1)
                    break

    if successfulProjectCounter < 2:
        project.append(0)

    # Get variables 'media', 'sustainability' and 'story'
    graphData = [{
        "operationName": "Campaign",
        "variables": {
            "slug": project[23]
        },
        "query": "query Campaign($slug: String!) {\n  project(slug: $slug) {\n    id\n    story\n}\n}\n"
    }]
    response = getOKResponse("https://www.kickstarter.com/graph", graphData)

    data = response.json()
    story = data[0]['data']['project']['story']
    if videoPitch:
        project.append(1)
    else:
        if "<img" in story or "class=\"video-player\"" in story:
            project.append(1)
        else:
            project.append(0)
    story = BeautifulSoup(story, 'lxml').text
    story = " ".join(story.split())
    story = story.encode('cp1252', 'ignore').decode('cp1252')
    if len(story) == 0:
        print(str(cntr) + "/" + str(len(projects)) + ": " + "skipped (empty story)")
        skippedWriter.write(str(project[0]) + "\n")
        continue
    if "sustainability" in story:
        project.append(1)
    else:
        project.append(0)
    project.append(story)

    dataWriter.writerow(project)
    print(str(cntr) + "/" + str(len(projects)) + ": " + str(project[25:30]))

session.close()
