# -*- coding: utf-8-sig -*-
import ssl
import time
import glob
import csv
import datetime
import sys
import shutil
import os
import requests
import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import Request, urlopen  # Web client
from selenium.webdriver.chrome.service import Service

sys.stdout.reconfigure(encoding='utf-8-sig')
ssl._create_default_https_context = ssl._create_unverified_context
start_time = datetime.datetime.now()
max_date = start_time-datetime.timedelta(45) #max_date is 42 days (6 weeks) from current date

print("Welcome to Tae's beautiful scraper")

# output file name
filename = "report-on.csv"
backup = filename[:len(filename)-4]+' - Copy.csv'
print("Current filename is "+filename+"\n")

# csv file header
headers = "Title,Salary,Company,Location,On-site/Remote,Date,Website,URL\n"

# Use this function to search for any files which matches the filename
file_present = glob.glob(filename)
backup_present = glob.glob(backup)

# this array contains all Title, Salary, Company and Location
data_Indeed = []
data_Indeed_writer = []

data_Jobrapido = []
data_Jobrapido_writer = []

data_Eluta = []
data_Eluta_writer = []

data_Linkedin = []
data_Linkedin_writer = []

data_Monster = []
data_Monster_writer = []

data_Workopolis = []
data_Workopolis_writer = []

data_Jobillico = []
data_Jobillico_writer = []

data_Google_jobs = []
data_Google_jobs_writer = []

data_Jobboom = []
data_Jobboom_writer = []

print("There are 4 cases of incoming data")
print("Data format is [Title, Salary, Company, Location, Date, Website, URL]")
print("we will refer to [Title, Salary, Company, Location] as mainData\n")

print("same URL same mainData, we do NOTHING, it's a duplicate !")
print("same URL different mainData, we UPDATE the mainData")
print("different URL different mainData, we ADD this")
print("different URL same mainData, we UPDATE the URL\n")

print("data_Website are tables containing the following :[Title, Salary, Company, Location, Date, Website, URL]")
print("data_Website_writer is used to format data_Website into a csv string")



#returns array of sub data useful for other functions
#example returns the URL for i = 6 and j = 7.
def getSubData(i, j, data_Website):
    return [item[i:j] for item in data_Website]

#adds [Title, Salary, Company, Location, On-site/Remote, Date, Website, URL] to data_Website
def taeAdd(data_Website, current_full_data):
    data_Website.append(current_full_data)

#data in data_Website is [Title, Salary, Company, Location, On-site/Remote, Date, Website, URL]
#current_data is [Title, Salary, Company, Location]
#removes data of data_Website with matching current_data
def taePopData(data_Website, current_data):
    index = getSubData(0, 5, data_Website).index(current_data)
    data_Website.pop(index)

#data in data_Website is [Title, Salary, Company, Location, On-site/Remote, Date, Website, URL]
#pUrl is an URL
#removes data of data_Website with matching pUrl
def taePopUrls(data_Website, pUrl):
    index = getSubData(7, 8, data_Website).index([pUrl])
    data_Website.pop(index)

#pUrl is the URL of the incoming data
#current_date is [Title, Salary, Company, Location]
#current_full_data is [Title, Salary, Company, Location, On-site/Remote, Date, Website, URL]
def taeDataCase(pUrl, current_data, current_full_data, data_Website):
    # current_full_data[5] is website name
    # current_full_data[0] is title
    # uncomment if trying to remove duplicates from raw data
    #current_data[1] = " ".join(((current_data[1]).strip()).split())
    #current_full_data[1] = current_data[1]

    if (current_full_data[0] == ""): # title not empty
        print("No title linked to the following data:", current_full_data)
    elif [pUrl] not in getSubData(7, 8, data_Website):         #URL does not exist
        if current_data not in getSubData(0, 5, data_Website): #Data does not exist
            taeAdd(data_Website, current_full_data)
            print("New data",current_full_data[6])
        else:                                                  #Data exist
            taePopData(data_Website, current_data)
            taeAdd(data_Website, current_full_data)
            print("Updating URL",current_full_data[6])
    else:                                                      #URL exist
        if current_data not in getSubData(0, 5, data_Website): #Data does not exist
            taePopUrls(data_Website, pUrl)
            taeAdd(data_Website, current_full_data)
            print("Updating data",current_full_data[6])
        else:                                                  #Data exist
            print("Duplicate",current_full_data[6])

#fixs most string errors
def taeLocation(pLocation):
    location = pLocation.replace('"',"'").replace(',','').replace('â','a').replace('ô','o').replace('Ã©','e').replace('é','e').replace('É','e').replace('è','e').replace('Ã´','o').replace('.','').replace('’',"'").replace('´',"'").replace("(","").replace(")","").replace("  "," ").replace("| ","").replace("/ ","").replace("–","-")
    location = location.replace('St ','Saint ').replace('Ste ','Sainte ').replace('St-','Saint-').replace('Ste-','Sainte-')
    location = location.replace("Niagara On The Lake","Niagara-on-the-Lake").replace('Barrys Bay',"Barry's Bay").replace('Burks Falls',"Burk's Falls").replace('Lions Head',"Lion's Head").replace("Greater Toronto Area Canada","Greater Toronto Area ON")
    location = location.replace('Cote-Saint-Luc','Cote Saint-Luc').replace('Dollard-Des-Ormeaux','Dollard-Des Ormeaux').replace('Dollard-des-Ormeaux','Dollard-Des Ormeaux').replace("Kitchener-Waterloo","Kitchener")
    location = location.replace('Saint-Lin - Laurentides','Saint-Lin-Laurentides').replace('Saint-Lin/Laurentides','Saint-Lin-Laurentides').replace('Saint-Lin--Laurentides','Saint-Lin-Laurentides').replace('Saint-Lin ','Saint-Lin-Laurentides ')
    location = location.replace("MONTREAL","Montreal").replace("Montreal (St Laurent)","Saint-Laurent").replace("MISSISSAUGA","Mississauga").replace("Mississauga Canada","Mississauga ON").replace("Blue Mountain ","Blue Mountains ").replace("The Blue Mountains ","Blue Mountains ")
    location = location.replace("Mississauga CA","Mississauga ON").replace("Greater Montreal Area QC","Montreal QC").replace("Greater Montreal QC","Montreal QC").replace("Lasalle","LaSalle").replace("Saint Laurent", "Saint-Laurent")
    location = location.replace("Montreal CA","Montreal QC").replace(" -","-").replace("- ","-")
    location = location.split(" +1 ")[0]
    if (len(location.split(" "))>2) and ("Montreal" in (location.split(" "))) and ("Old" not in location) and ("Nord" not in location) and ("city" not in location):
        location = location.split(" ")
        location.remove("Montreal")
        location = " ".join(location)
    if (len(location.split(" "))>2) and ("Quebec" in (location.split(" "))) and ("de Quebec" not in location) and ("city" not in location):
        location = location.split(" ")
        location.remove("Quebec")
        location = " ".join(location)
    if location == "ON":
        location = "Ontario"
    if location == "ON ON":
        location = "Ontario"
    if location == "QC":
        location = "Quebec"
    if location == "QC QC":
        location = "Quebec"
    location.replace(' in ',' ');
    if location.startswith("in "):
        location = location[3:]
    return location

#removes all data more than 42 days old (6 weeks)
#sorts the data from newest to oldest date
#formats data_Website into a csv string named data_Website_writer
def taeWriteSorted(data_Website, data_Website_writer):
    data_Website = [row for row in data_Website if datetime.datetime.strptime(row[5][0:],"%a %d %b %Y") >= max_date-datetime.timedelta(1)]
    data_Website = sorted(data_Website, key = lambda row: datetime.datetime.strptime(row[5][0:],"%a %d %b %Y"), reverse=True)
    for row in data_Website:
        data_Website_writer.append('"'+'","'.join(row)+'"')


#returns first number or 0 if string does not contain numbers
def getFirstNumber(daysStr):
    nList = [int(s) for s in daysStr.split() if s.isdigit()]
    if not nList:
        days = 0
        if ("Just" not in daysStr) and ("Hiring" not in daysStr) and ("Today" not in daysStr):
            print(daysStr)
    else:
        days = nList[0]
    return days

def findWorktype(text):
    text = text.lower();
    if "hybrid" in text and "remote" in text:
        return "Hybrid Remote"
    elif "remote" in text:
        return "Remote"
    elif "hybrid" in text:
        return "Hybrid"
    else:
        return ""

#if filename does not exist, create it
if not file_present:
    print("The file DOES NOT exist, all tables are empty and initialized")
else:

    #if backupfile exists
    if backup_present:
        filename_size = os.stat(filename).st_size
        backup_size = os.stat(backup).st_size
        print('filename size',filename_size)
        print('backup size',backup_size)
        if backup_size>filename_size:
            print("Backup file is bigger than file, Backup file '"+backup+"' is not overwritten\n")
        else:
            shutil.copyfile(filename, backup)
            print("Overwritting backup file '"+backup+"'\n")
    else:
        shutil.copyfile(filename, backup)
        print("Backup file does not exist and is created backup file '"+backup+"'\n")

    #reads csv file and add data their respective data_Website
    with open(filename,"r", encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',',quoting=csv.QUOTE_ALL, skipinitialspace=True)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print('Column names are '+(','.join(row)))
                line_count += 1
            else:
                website = ''.join(row[6:7])
                if (len(row)>3):
                    row[3] = taeLocation(row[3]).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ','')
                    if (website == "Indeed"):
                        data_Indeed.append(row)
                    elif (website == "Jobrapido"):
                        data_Jobrapido.append(row)
                    elif (website == "Eluta"):
                        data_Eluta.append(row)
                    elif (website == "Linkedin"):
                        data_Linkedin.append(row)
                    elif (website == "Monster"):
                        data_Monster.append(row)
                    elif (website == "Workopolis"):
                        row, data_Workopolis.append(row)
                    elif (website == "Jobillico"):
                        data_Jobillico.append(row)
                    elif (website == "Google jobs"):
                        data_Google_jobs.append(row)
#                   elif (website == "Jobboom"):
#                        data_Jobboom.append(row)
                    else:
                        print(website)
                line_count += 1
        csv_file.close()
    print(str(line_count)+" lines are being processed")

    data_lines = len(data_Indeed) + len(data_Jobrapido) + len(data_Eluta) + len(data_Linkedin) + len(data_Monster) + len(data_Workopolis) + len(data_Jobillico) + len(data_Google_jobs) + len(data_Jobboom)
    if (data_lines==0):
        print("File exists but no data, tables are empty and initialized")
    else:
        if (len(data_Indeed)>0):
            print("First full_data in the table is ",str(data_Indeed[0]).encode().decode())
        elif (len(data_Jobrapido)>0):
            print("First full_data in the table is ",str(data_Jobrapido[0]).encode().decode())
        elif (len(data_Eluta)>0):
            print("First full_data in the table is ",str(data_Eluta[0]).encode().decode())
        elif (len(data_Linkedin)>0):
            print("First full_data in the table is ",str(data_Linkedin[0]).encode().decode())
        elif (len(data_Monster)>0):
            print("First full_data in the table is ",str(data_Monster[0]).encode().decode())
        elif (len(data_Workopolis)>0):
            print("First full_data in the table is ",str(data_Workopolis[0]).encode().decode())
        elif (len(data_Jobillico)>0):
            print("First full_data in the table is ",str(data_Jobillico[0]).encode().decode())
        elif (len(data_Google_jobs) >0):
            print("First full_data in the table is ",str(data_Google_jobs[0]).encode().decode())
#       elif (len(data_Jobboom)>0):
#           print("First full_data in the table is ",str(data_Jobboom[0]).encode().decode())
        else:
            print("what the hell")

'''
cap_Indeed = 0 #25
cap_Jobrapido = 0 #30
cap_Stackoverflow = 0 #5
cap_Eluta = 0 #100
cap_Workopolis = 0 #50
cap_Jobillico = 0 #60
cap_Linkedin = 0 #50
cap_Monster = 0 #50
cap_Jobboom = 0 #60
cap_Google_jobs = 0 #30

cap_Indeed = 25 #25
cap_Jobrapido = 30 #30
cap_Stackoverflow = 5 #5
cap_Eluta = 100 #100
cap_Workopolis = 50 #50
cap_Jobillico = 60 #60
cap_Linkedin = 50 #50
cap_Monster = 50 #50
cap_Jobboom = 60 #60
cap_Google_jobs = 30 #30
'''

cap_Indeed = 25 #25
cap_Jobrapido = 32 #32
#cap_Workopolis = 5 #50
cap_Jobillico = 30 #30
cap_Linkedin = 50 #50
cap_Monster = 15 #15
#cap_Jobboom = 30 #60

max_attempts = 2

options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(use_subprocess=True, options=options)

page_url_Indeed = "https://ca.indeed.com/jobs?l=Ontario"
driver.get(page_url_Indeed)
i=0
attempt = 0

while (i<cap_Indeed):
    page_url_Indeed = "https://ca.indeed.com/jobs?l=Ontario&sort=date&limit=50&start="+str(50*i)
    driver.get(page_url_Indeed)

    try:
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-gnav-element-name='Logo']")))
        
        posts = [] #job postings array
        attempt = 0

        while (attempt < max_attempts and len(posts)==0):
            posts = driver.find_elements('css selector', 'div[class="job_seen_beacon"]')
            attempt += 1
            print("\n"+str(len(posts))+" jobs processed for page "+str(i)+", attempt #"+str(attempt))

        for post in posts:
            pTitle = ''
            titles = post.find_elements('tag name', 'span')
            for title in titles:
                if title.get_attribute('title') != "":
                    pTitle = title.get_attribute('title')
            
            if pTitle != '':
                pSalary = ''
                pCompany = ''
                pLocation = ''
                pUrl = ''

                if post.find_elements('css selector', 'div[class="metadata salary-snippet-container"]'):
                    pSalary = post.find_element('css selector', 'div[class="metadata salary-snippet-container"]').get_attribute("innerText").replace('–',' - ').replace('"',"'").strip()
                    t = pSalary.split(' ')
                    if 'K' in t:
                        t = t.replace('$', '$ ')
                        pTime = t.split(' ')
                        for idx, s in enumerate(pTime):
                            if 'K' in s:
                                pTime[idx] = str(int(float(s.replace('K',''))*1000))

                        pSalary = ' '.join(pTime).replace('$ ', '$')

                if post.find_elements('css selector', 'span[class="date"]'):
                    daysStr = post.find_element('css selector', 'span[class="date"]').get_attribute("innerText").strip()
                    days = getFirstNumber(daysStr)
                else:
                    days = 0

                if post.find_elements('css selector', 'a[data-tn-element="companyName"]'):
                    pCompany = post.find_element('css selector', 'a[data-tn-element="companyName"]').get_attribute("innerText").strip()
                else:
                    if post.find_elements('css selector', 'span[class="companyName"]'):
                        pCompany = post.find_element('css selector', 'span[class="companyName"]').get_attribute("innerText").strip()

                if post.find_elements('css selector', 'div[class="companyLocation"]'):
                    pLocation = taeLocation(post.find_element('css selector', 'div[class="companyLocation"]').get_attribute("innerText").strip())
                    if "+" in pLocation:
                        pLocation = pLocation.split("+")
                        pLocation = str(pLocation[0])
                    if "•" in pLocation:
                        pLocation = pLocation.split("•")
                        pLocation = str(pLocation[0])
                    pLocation = pLocation.replace('\n','')

                if post.find_elements('css selector', "a[id^='sj_']"):
                    pUrl = post.find_element('css selector', "a[id^='sj_']").get_attribute('href')
                else:
                    if post.find_elements('css selector', "a[id^='job_']"):
                        pUrl = post.find_element('css selector', "a[id^='job_']").get_attribute('href')

                if pUrl != "":
                    hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
                    if hybridremote == "":
                        hybridremote = findWorktype(pTitle)
                    current_data = [pTitle.replace('"',"'").replace('=',''),pSalary,pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
                    taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()-datetime.timedelta(days)).strftime("%a %d %b %Y"),'Indeed',pUrl], data_Indeed)
    except TimeoutException:
        attempt += 1
        print("\n page "+str(i)+", attempt #"+str(attempt)+" is unsucessful")
    finally:
        i=i+1

driver.close()
driver.quit()


pSalary = ''
i=0
while (i<cap_Jobrapido):
    i=i+1
    page_url = "https://ca.jobrapido.com/Jobs-in-Ontario?p="+str(i)+"&sortby=publish_date"
    posts = []
    attempt = 0
    while (attempt < max_attempts and len(posts)==0):
        req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            webpage = urlopen(req, timeout = 15).read()
            time.sleep(2)
            page_soup = soup(webpage.decode('utf-8-sig'),"html.parser")
            page_soup.prettify()
            posts = page_soup.findAll("div", {"class": "result-item__wrapper"})
        except TimeoutException:
            print("\n page "+str(i)+", attempt #"+str(attempt)+" is unsucessful")
            attempt += 1
        finally:
            attempt += 1
            print("\n"+str(len(posts))+" jobs processed for page "+str(i)+", attempt #"+str(attempt))

    for post in posts:
        pTitle = ""
        pCompany = ""
        pLocation = ""
        pUrl = ""

        pTitle = post.find("div", {"class":"result-item__title"}).text.strip()

        if (len(post.findAll("span", {"class":"result-item__company-label"}))>0):
            pCompany = post.find("span", {"class":"result-item__company-label"}).text.strip()

        if (len(post.findAll("span", {"class":"result-item__location-label"}))>0):
            pLocation = post.find("span", {"class":"result-item__location-label"}).text.strip()
            if "(" in pLocation:
                pLocation = taeLocation(pLocation.replace('(',' ').replace(')',' ').replace("Toronto","").replace("Mississauga",""))
                pLocation = pLocation.split(" ")
                pLocation[:] = [x for x in pLocation if x]
                pLocation = list(set(pLocation))
                pLocation.sort()
                pLocation = " ".join(pLocation)+" ON"

        daysStr = str(post.find("div", {"class":"result-item__date"}).text.strip()+datetime.datetime.now().strftime(" %Y"))
        pUrl = post.find("a", {"class":"result-item__link"})["href"].replace('"','|')

        hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
        if hybridremote == "":
            hybridremote = findWorktype(pTitle)
        current_data = [pTitle.replace('"',"'").replace('=',''),"",pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
        taeDataCase(pUrl, current_data, current_data+[datetime.datetime.strptime(daysStr,"%d %b %Y").strftime("%a %d %b %Y"),"Jobrapido",pUrl], data_Jobrapido)


pSalary = ''
i=0
while (i<cap_Jobillico):
    i=i+1
    page_url = "https://www.jobillico.com/search-jobs?skwd=&scty=toronto&icty=4943&mfil=15&sort=date&ipg="+str(i)
    posts = []
    attempt = 0
    while (attempt < max_attempts and len(posts)==0):
        req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            webpage = urlopen(req, timeout = 15).read()
            time.sleep(2)
            page_soup = soup(webpage.decode('utf-8-sig'),"html.parser")
            page_soup.prettify()
            posts = page_soup.find_all("article", ref=lambda x: x and x.startswith("job"))
        except TimeoutException:
            print("\n page "+str(i)+", attempt #"+str(attempt)+" is unsucessful")
            attempt += 1
        finally:
            attempt += 1
            print("\n"+str(len(posts))+" jobs processed for page "+str(i)+", attempt #"+str(attempt))

    for post in posts:
        pTitle = ""
        pSalary = ""
        pCompany = ""
        pLocation = ""

        if (len(post.findAll("h2", {"class":"h3 pr4"}))>0):
            pTitle = post.find("h2", {"class":"h3 pr4"}).text.strip()

            if (len(post.findAll("a", {"class":"link companyLink"}))>0):
                pCompany = post.find("a", {"class":"link companyLink"}).text.strip()

            if (len(post.findAll("p", {"class":"inline xs"}))>0):
                pLocation = post.find("p", {"class":"inline xs"}).text.strip()
                pLocation = pLocation.replace(' - '," ")

            if (len(post.findAll("time", {"class":"xs"}))>0):
                daysStr = post.find("time", {"class":"xs"}).text.strip()
                daysStr = daysStr.split(" ")
                if "today" in daysStr:
                    days = 0
                elif "day(s)" in daysStr:
                    daysStr = daysStr[0]
                    if ((daysStr.replace(" ","")).isdigit()):
                        days = int(daysStr)
                    else:
                        days = 0
                        print('has days but no #',daysStr)
                else:
                    days = 0
                    print('no today, no days, no #',daysStr)
            else:
                days = 0
            
            website = post.find("h2", {"class":"h3 pr4"})
            if website:
                link = website.find("a", href=True)
                if link:
                    pUrl = "https://www.jobillico.com"+link['href']
                    
            hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
            if hybridremote == "":
                hybridremote = findWorktype(pTitle)
            current_data = [pTitle.replace('"',"'").replace('=',''),"",pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
            taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()-datetime.timedelta(days)).strftime("%a %d %b %Y"),"Jobillico",pUrl], data_Jobillico)


pSalary = ''
i=0
while (i<cap_Jobillico):
    i=i+1
    page_url = "https://www.jobillico.com/search-jobs?skwd=&scty=mississauga&icty=4624mfil=40&sort=date&ipg="+str(i)
    posts = []
    attempt = 0
    while (attempt < max_attempts and len(posts)==0):
        req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            webpage = urlopen(req, timeout = 15).read()
            time.sleep(2)
            page_soup = soup(webpage.decode('utf-8-sig'),"html.parser")
            page_soup.prettify()
            posts = page_soup.find_all("article", ref=lambda x: x and x.startswith("job"))
        except TimeoutException:
            print("\n page "+str(i)+", attempt #"+str(attempt)+" is unsucessful")
            attempt += 1
        finally:
            attempt += 1
            print("\n"+str(len(posts))+" jobs processed for page "+str(i)+", attempt #"+str(attempt))

    for post in posts:
        pTitle = ""
        pSalary = ""
        pCompany = ""
        pLocation = ""

        if (len(post.findAll("h2", {"class":"h3 pr4"}))>0):
            pTitle = post.find("h2", {"class":"h3 pr4"}).text.strip()

            if (len(post.findAll("a", {"class":"link companyLink"}))>0):
                pCompany = post.find("a", {"class":"link companyLink"}).text.strip()

            if (len(post.findAll("p", {"class":"inline xs"}))>0):
                pLocation = post.find("p", {"class":"inline xs"}).text.strip()
                pLocation = pLocation.replace(' - '," ")

            if (len(post.findAll("time", {"class":"xs"}))>0):
                daysStr = post.find("time", {"class":"xs"}).text.strip()
                daysStr = daysStr.split(" ")
                if "today" in daysStr:
                    days = 0
                elif "day(s)" in daysStr:
                    daysStr = daysStr[0]
                    if ((daysStr.replace(" ","")).isdigit()):
                        days = int(daysStr)
                    else:
                        days = 0
                        print('has days but no #',daysStr)
                else:
                    days = 0
                    print('no today, no days, no #',daysStr)
            else:
                days = 0
            
            website = post.find("h2", {"class":"h3 pr4"})
            if website:
                link = website.find("a", href=True)
                if link:
                    pUrl = "https://www.jobillico.com"+link['href']
                    
            hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
            if hybridremote == "":
                hybridremote = findWorktype(pTitle)
            current_data = [pTitle.replace('"',"'").replace('=',''),"",pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
            taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()-datetime.timedelta(days)).strftime("%a %d %b %Y"),"Jobillico",pUrl], data_Jobillico)

            
options = uc.ChromeOptions()
options.headless = True
driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager().install())) 
driver.maximize_window()

page_url_linkedin1 = "https://ca.linkedin.com/jobs/linkedin-jobs?position=1&pageNum=0"
page_url_linkedin2 = "https://www.linkedin.com/jobs/search?keywords=&location=Ontario%2C%20Canada&sortBy=DD&f_TPR=r86400&position=1&pageNum=0"

driver.get(page_url_linkedin1)
time.sleep(3)
driver.get(page_url_linkedin2)
time.sleep(3)

h1 = driver.execute_script("return document.body.scrollHeight")
i = 0
while i<cap_Linkedin:
    print('Currently scrolling page',str(i),'of Linkedin')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    h2 = driver.execute_script("return document.body.scrollHeight")
    if h1==h2:
        if driver.find_elements('css selector', 'button.infinite-scroller__show-more-button.infinite-scroller__show-more-button--visible'):
            button = driver.find_element('css selector', 'button.infinite-scroller__show-more-button.infinite-scroller__show-more-button--visible')
            ActionChains(driver).move_to_element(button).click(button).perform()
            time.sleep(3)
            h2 = driver.execute_script("return document.body.scrollHeight")
        else:
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print('ya aint shit')
            h2 = driver.execute_script("return document.body.scrollHeight")
    h1=h2
    i = i+1

posts = driver.find_elements('css selector', 'div.base-card.base-card--link.base-search-card.base-search-card--link.job-search-card')
time.sleep(5)

for post in posts:
    if post.find_elements('css selector', "time[class^='job-search-card__listdate']"):
        pTitle = post.find_element('css selector', 'h3.base-search-card__title').get_attribute("innerText").strip()
        pSalary = ""
        if post.find_elements('css selector', 'span.job-search-card__salary-info'):
            pSalary = " ".join((post.find_element('css selector', 'span.job-search-card__salary-info').get_attribute("innerText").strip().replace('"',"'")).split())
        pTime = post.find_element('css selector', "time[class^='job-search-card__listdate']").get_attribute('datetime')
        pCompany = post.find_element('css selector', 'h4.base-search-card__subtitle').get_attribute("innerText").strip()
        pLocation = taeLocation(post.find_element('css selector', 'span.job-search-card__location').get_attribute("innerText").strip().replace("Quebec, Canada","QC"))
        pUrl = post.find_element('css selector', 'a.base-card__full-link').get_attribute('href')

        hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
        if hybridremote == "":
            hybridremote = findWorktype(pTitle)
        current_data = [pTitle.replace('"',"'").replace('=',''),pSalary,pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
        taeDataCase(pUrl, current_data, current_data+[datetime.datetime.strptime(pTime,"%Y-%m-%d").strftime("%a %d %b %Y"),"Linkedin",pUrl], data_Linkedin)
driver.close()
driver.quit()


options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(use_subprocess=True, options=options)

page_url_Monster = "https://www.monster.ca"
driver.get(page_url_Monster)
time.sleep(3)

page_url_Monster = "https://www.monster.ca/jobs/l-toronto-on"
driver.set_window_size(600, 1000)
driver.get(page_url_Monster)
time.sleep(3)

h1 = driver.execute_script("return document.body.scrollHeight")
i = 0
while i<cap_Monster:
    print('Currently scrolling page',str(i),'of Monster')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    h2 = driver.execute_script("return document.body.scrollHeight")
    if h1==h2:
        if driver.find_elements('css selector', 'button[class="sc-dkPtyc hVjBwZ  ds-button"'):
            button = driver.find_element('css selector', 'button[class="sc-dkPtyc hVjBwZ  ds-button"')
            ActionChains(driver).move_to_element(button).click(button).perform()
            time.sleep(3)
            h2 = driver.execute_script("return document.body.scrollHeight")
        else:
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print('ya aint shit')
            h2 = driver.execute_script("return document.body.scrollHeight")
    h1=h2
    i = i+1

posts = driver.find_elements('css selector', 'article[data-test-id^="svx-job-card-component-"]')
time.sleep(5)

for post in posts:
    
    if post.find_elements('css selector', 'a[data-testid="jobTitle"]'):
        pSalary = ''
        pCompany = ''
        pLocation = ''
        pUrl = ''
        pTitle = post.find_element('css selector', 'a[data-testid="jobTitle"]').get_attribute("innerText").strip()

        if post.find_elements('css selector', 'div[data-tagtype-testid="payTag"]'):
            pSalary = post.find_element('css selector', 'div[data-tagtype-testid="payTag"]').get_attribute("innerText").strip().replace(" /"," ").replace('"',"'").replace('Per Year','a year').replace('Per Hour','an hour').replace('Per Week','a week').replace('Per Month','a month')
            pSalary = pSalary.split(' ')
            j = 0
            while j < len(pSalary):
                if (('k' in pSalary[j]) and ('week' not in pSalary[j])):
                    pSalary[j] = (pSalary[j]).replace('k','').replace('$','')
                    pSalary[j] = '$'+"{:,}".format(int(float(pSalary[j])*1000))
                j = j + 1
            pSalary = ' '.join(pSalary)

        if post.find_elements('css selector', 'span[data-testid="jobDetailDateRecency"]'):
            pTime = post.find_element('css selector', 'span[data-testid="jobDetailDateRecency"]').get_attribute("innerText").strip()

        if pTime=="Today":
            days = 0
        else:
            if ((pTime[0:2].replace(" ","")).isdigit()):
                days = int(pTime[0:2])
            else:
                days = 0
                print(pTime)

        if post.find_elements('css selector', 'span[data-testid="company"]'):
            pCompany = post.find_element('css selector', 'span[data-testid="company"]').get_attribute("innerText").strip()

        if post.find_elements('css selector', 'span[data-testid="jobDetailLocation"]'):
            pLocation = taeLocation(post.find_element('css selector', 'span[data-testid="jobDetailLocation"]').get_attribute("innerText").strip())
            if len(pLocation.split(' '))==1 and not pLocation.split(" ") == [""]:
                pLocation = pLocation+' QC'

        pUrl = post.find_element('css selector', 'a[data-testid="jobTitle"]').get_attribute('href')

        hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
        if hybridremote == "":
            hybridremote = findWorktype(pTitle)
        current_data = [pTitle.replace('"',"'").replace('=',''),pSalary,pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
        taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()-datetime.timedelta(days)).strftime("%a %d %b %Y"),"Monster",pUrl], data_Monster)

driver.close()
driver.quit()


options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(use_subprocess=True, options=options)

page_url_Monster = "https://www.monster.ca"
driver.get(page_url_Monster)
time.sleep(3)

page_url_Monster = "https://www.monster.ca/jobs/l-mississauga-on"
driver.set_window_size(600, 1000)
driver.get(page_url_Monster)
time.sleep(3)

h1 = driver.execute_script("return document.body.scrollHeight")
i = 0
while i<cap_Monster:
    print('Currently scrolling page',str(i),'of Monster')
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    h2 = driver.execute_script("return document.body.scrollHeight")
    if h1==h2:
        if driver.find_elements('css selector', 'button[class="sc-dkPtyc hVjBwZ  ds-button"'):
            button = driver.find_element('css selector', 'button[class="sc-dkPtyc hVjBwZ  ds-button"')
            ActionChains(driver).move_to_element(button).click(button).perform()
            time.sleep(3)
            h2 = driver.execute_script("return document.body.scrollHeight")
        else:
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print('ya aint shit')
            h2 = driver.execute_script("return document.body.scrollHeight")
    h1=h2
    i = i+1

posts = driver.find_elements('css selector', 'article[data-test-id^="svx-job-card-component-"]')
time.sleep(5)

for post in posts:
    
    if post.find_elements('css selector', 'a[data-testid="jobTitle"]'):
        pSalary = ''
        pCompany = ''
        pLocation = ''
        pUrl = ''
        pTitle = post.find_element('css selector', 'a[data-testid="jobTitle"]').get_attribute("innerText").strip()

        if post.find_elements('css selector', 'div[data-tagtype-testid="payTag"]'):
            pSalary = post.find_element('css selector', 'div[data-tagtype-testid="payTag"]').get_attribute("innerText").strip().replace(" /"," ").replace('"',"'").replace('Per Year','a year').replace('Per Hour','an hour').replace('Per Week','a week').replace('Per Month','a month')
            pSalary = pSalary.split(' ')
            j = 0
            while j < len(pSalary):
                if (('k' in pSalary[j]) and ('week' not in pSalary[j])):
                    pSalary[j] = (pSalary[j]).replace('k','').replace('$','')
                    pSalary[j] = '$'+"{:,}".format(int(float(pSalary[j])*1000))
                j = j + 1
            pSalary = ' '.join(pSalary)

        if post.find_elements('css selector', 'span[data-testid="jobDetailDateRecency"]'):
            pTime = post.find_element('css selector', 'span[data-testid="jobDetailDateRecency"]').get_attribute("innerText").strip()

        if pTime=="Today":
            days = 0
        else:
            if ((pTime[0:2].replace(" ","")).isdigit()):
                days = int(pTime[0:2])
            else:
                days = 0
                print(pTime)

        if post.find_elements('css selector', 'span[data-testid="company"]'):
            pCompany = post.find_element('css selector', 'span[data-testid="company"]').get_attribute("innerText").strip()

        if post.find_elements('css selector', 'span[data-testid="jobDetailLocation"]'):
            pLocation = taeLocation(post.find_element('css selector', 'span[data-testid="jobDetailLocation"]').get_attribute("innerText").strip())
            if len(pLocation.split(' '))==1 and not pLocation.split(" ") == [""]:
                pLocation = pLocation+' QC'

        pUrl = post.find_element('css selector', 'a[data-testid="jobTitle"]').get_attribute('href')

        hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
        if hybridremote == "":
            hybridremote = findWorktype(pTitle)
        current_data = [pTitle.replace('"',"'").replace('=',''),pSalary,pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
        taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()-datetime.timedelta(days)).strftime("%a %d %b %Y"),"Monster",pUrl], data_Monster)

driver.close()
driver.quit()

pSalary = ''
i=0
page_url = "https://www.jobboom.com/en"
session = requests.Session()
webpage = session.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, verify=True).content
time.sleep(2)
while (i<cap_Jobboom):

    i=i+1
    page_url = "https://www.jobboom.com/en/toronto-city-of/_r31-"+str(i)+"?sortBy=date"
    
    posts = []
    attempt = 0
    while (attempt < max_attempts and len(posts)==0):
        webpage = session.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, verify=True).content
        time.sleep(2)
        page_soup = soup(webpage.decode('utf-8-sig'),"html.parser")
        page_soup.prettify()

        posts = page_soup.find_all("div", {"class":["job_item","job_item_video"]})

        attempt += 1
        print("\n"+str(len(posts))+" jobs processed for page "+str(i)+", attempt #"+str(attempt))

    for post in posts:
        pCompany = ''
        pLocation = ''

        link_title = post.find("p", {"class":"offre"}).find("a", href=True)
        pTitle = link_title['title']
        
        if (len(post.findAll("p", {"class":'employeur'}))>0):
            pCompany = post.find("p", {"class":'employeur'}).find("span").text.strip()

        if (len(post.findAll("span", {"class":"jobCityProv"}))>0):
            pLocation = post.find("span", {"class":"jobCityProv"}).text.strip()
        elif (len(post.findAll("span", {"class":"bold"}))>0):
            pLocation = post.find("span", {"class":"bold"}).text.strip().replace(',',' ')
        pLocation = pLocation.replace('(Region de)','').replace('(Région de)','').replace('(Region)','QC').replace('(Région)','QC').replace('Quebec Montreal QC','Montreal QC')
        pLocation = pLocation.replace('Montreal / Saint Laurent','Saint Laurent')

        if '(' in pLocation:
            pLocation = pLocation.split('(')[0]

        pUrl = "https://www.jobboom.com"+link_title['href']

        current_data = [pTitle.replace('"',"'").replace('=',''),"",pCompany.replace('"',"'"),taeLocation(pLocation)]
        taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()).strftime("%a %d %b %Y"),"Jobboom",pUrl], data_Jobboom)
session.close()

'''
pSalary = ''
i=0
page_url = "https://www.jobboom.com/en"
session = requests.Session()
webpage = session.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, verify=True).content
time.sleep(2)
while (i<cap_Jobboom):

    i=i+1
    page_url = "https://www.jobboom.com/en/gta-mississauga-oshawa/_r87-"+str(i)+"?sortBy=date"
    
    posts = []
    attempt = 0
    while (attempt < max_attempts and len(posts)==0):
        webpage = session.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, verify=True).content
        time.sleep(2)
        page_soup = soup(webpage.decode('utf-8-sig'),"html.parser")
        page_soup.prettify()

        posts = page_soup.find_all("div", {"class":["job_item","job_item_video"]})

        attempt += 1
        print("\n"+str(len(posts))+" jobs processed for page "+str(i)+", attempt #"+str(attempt))

    for post in posts:
        pCompany = ''
        pLocation = ''

        link_title = post.find("p", {"class":"offre"}).find("a", href=True)
        pTitle = link_title['title']
        
        if (len(post.findAll("p", {"class":'employeur'}))>0):
            pCompany = post.find("p", {"class":'employeur'}).find("span").text.strip()

        if (len(post.findAll("span", {"class":"jobCityProv"}))>0):
            pLocation = post.find("span", {"class":"jobCityProv"}).text.strip()
        elif (len(post.findAll("span", {"class":"bold"}))>0):
            pLocation = post.find("span", {"class":"bold"}).text.strip().replace(',',' ')
        pLocation = pLocation.replace('(Region de)','').replace('(Région de)','').replace('(Region)','QC').replace('(Région)','QC').replace('Quebec Montreal QC','Montreal QC')
        pLocation = pLocation.replace('Montreal / Saint Laurent','Saint Laurent')

        if '(' in pLocation:
            pLocation = pLocation.split('(')[0]

        pUrl = "https://www.jobboom.com"+link_title['href']

        hybridremote = findWorktype(taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''))
        if hybridremote == "":
            hybridremote = findWorktype(pTitle)
        current_data = [pTitle.replace('"',"'").replace('=',''),"",pCompany.replace('"',"'"),taeLocation(pLocation).replace('Remote ','').replace('remote ','').replace('Hybrid ','').replace('Hybride ','').replace('hybrid ','').replace('hybride ',''),hybridremote]
        taeDataCase(pUrl, current_data, current_data+[(datetime.datetime.now()).strftime("%a %d %b %Y"),"Jobboom",pUrl], data_Jobboom)
session.close()
'''

# opens and writes file
with open(filename,"w", encoding='utf-8-sig') as f:
    f.write(headers)

    if (len(data_Indeed)>0):
        taeWriteSorted(data_Indeed, data_Indeed_writer)
        f.write((str('\n'.join(data_Indeed_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Indeed")
    if (len(data_Jobrapido)>0):
        taeWriteSorted(data_Jobrapido, data_Jobrapido_writer)
        f.write((str('\n'.join(data_Jobrapido_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Jobrapido")
    if (len(data_Workopolis)>0):
        taeWriteSorted(data_Workopolis, data_Workopolis_writer)
        f.write((str('\n'.join(data_Workopolis_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Workopolis")
    if (len(data_Jobillico)>0):
        taeWriteSorted(data_Jobillico, data_Jobillico_writer)
        f.write((str('\n'.join(data_Jobillico_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Jobillico")
    if (len(data_Linkedin)>0):
        taeWriteSorted(data_Linkedin, data_Linkedin_writer)
        f.write((str('\n'.join(data_Linkedin_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Linkedin")
    if (len(data_Monster)>0):
        taeWriteSorted(data_Monster, data_Monster_writer)
        f.write((str('\n'.join(data_Monster_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Monster")
        '''
    if (len(data_Jobboom)>0):
        taeWriteSorted(data_Jobboom, data_Jobboom_writer)
        f.write((str('\n'.join(data_Jobboom_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Jobboom")'''
    if (len(data_Google_jobs)>0):
        taeWriteSorted(data_Google_jobs, data_Google_jobs_writer)
        f.write((str('\n'.join(data_Google_jobs_writer))).encode().decode()+'\n')
    else:
        print("Empty data file for Google jobs")

    f.close()  # Close the file


end_time = datetime.datetime.now()
total_time = end_time - start_time
minutes = divmod(total_time.total_seconds(), 60) 
print("\nStarted at "+start_time.strftime("%c")+", Ended at "+end_time.strftime("%c")+"\nTotal time is "+str(int(minutes[0]))+' minutes and '+str(int(minutes[1]))+' seconds')
print('Oldest date allowed is',max_date.strftime("%a %d %b %Y"))

#taskkill /im chromedriver.exe /f
# reminder fix hard coded +" ON"
