# ---------------------------------------------------------------------------------------------------------------------------------------------
# Code written and updated by : Renji David Ong (TR-PH-INTRN) 
# Results Verified by:          Junard Febrer (TR-PH-INTRN)
# Last Update: 09/10/22 11:32PM
# ---------------------------------------------------------------------------------------------------------------------------------------------
import requests 
from bs4 import BeautifulSoup
import re
import time
import csv
import datetime
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import json
import multiprocessing 
import os



#bn_howtofixguide Globalvar
sharedList = []
nLastLink = ""
linkCtr = 0
#bn_howtofixguide Global variable locks
shared_resource_lock=threading.Lock()
link_ctr_lock = threading.Lock()


#GLOBAL RESOURCES 
global_resource_lock = threading.Lock()
global_list = []
lastLinksJSON = {}

def checkLink(String):
    temp = verifyLink(String)
    blackList = [".txt", ".exe", "@", "e.g.", ".jpg", ".png", ".virus"]
    if temp:
        for i in blackList:
            if i in temp.lower():
                return False
    return temp
def verifyLink(string):
    httpsRegEx= r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    httpRegEx= r"http?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    wwwRegEx= r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    longDomain = r"^((?!-))(xn--)?[a-zA-Z0-9][a-zA-Z0-9-_]{0,61}[a-zA-Z0-9]{0,1}\.(xn--)?([a-zA-Z0-9\-]{1,61}|[a-zA-Z0-9]{1,30}\.[a-zA-Z]{2,})$"
    #regex find URL from dump
    if re.search(httpsRegEx,string):
        return re.search(httpsRegEx,string).group()
    elif re.search(httpRegEx,string):
        return re.search(httpRegEx,string).group()
    elif re.search(wwwRegEx, string):
        return re.search(wwwRegEx, string).group()
    elif re.search(longDomain, string):
        return re.search(longDomain, string).group()
    return False
def saveData():
    global global_list
    global lastLinksJSON
    try:
        print("Saving last Links...")
        with open("lastLinks.json", "w") as f:
            f.write(json.dumps(lastLinksJSON))
        print("Last Link JSON Saved in: lastLink.json\n")
    except Exception as e:
        print(e)
        name = str(datetime.datetime.now()).replace(":", "-").split(".")
        name = name[0] + "-" + name[1][:4]
        name = name.replace("-", "").replace(" ", "") + "lastLink.json"
        print("Last Link Retrieved Saved in: " + name + "\n")
        with open(name, "w") as f:
            f.write(nLastLink)
            
    try:
        print("Saving Collected Links...")
        if len(global_list):
            with open("out.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(global_list)
                
            print("Saved!")
            print("New File Name: out.csv")
        else:
            print("Nothing new to save")
    except Exception as e:
        print(e)
    
        print("Trying Again...")
        name = str(datetime.datetime.now()).replace(":", "-").split(".")
        name = name[0] + "-" + name[1][:4]
        name = name.replace("-", "").replace(" ", "") + "out.csv"
        
        if len(global_list):
            with open(name, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(global_list)
            print("Saved!")
            print("New File Name: "+name)
        else:
            print("Nothing new to save")

def saveToCache(name, data, nLastLink):
    global global_list
    global lastLinksJSON
    global_list += data
    lastLinksJSON[name] = nLastLink

    
def getLastLink():
    try:
        with open("lastLinks.json") as f:
            lastLinksJSON = json.load(f)
            return lastLinksJSON
    except Exception as e:
        print(e) 

def bn_malwaretipsScrape(n, sharedVar, name, lastLink):
    PATH = Service("chromedriver.exe")
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = options, service=PATH)
    
    global lastLinksJSON
    link = "https://malwaretips.com/blogs/category/adware/page/"
    pageCtr = 1
    lastPage = 1 
    newLinkList = []
    go = True
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        driver.get(actualLink)
        linkList = driver.find_elements(By.TAG_NAME, "article")
        for i in linkList:
            scamLink = checkLink(i.text)
            if scamLink:
                if scamLink == lastLink:
                    lastPage = pageCtr
                    go = False
                    break
                else:
                    newLinkList.append([name,scamLink])
        pageCtr+=1
    if len(newLinkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(newLinkList)} New Link(s) from {lastPage} page(s)")
        
        sharedVar[n] = [name, newLinkList, newLinkList[0][1]]

def bn_computipsScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://www.computips.org/category/removal-guides/adware/page/"
    nLink = False
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("h2", class_ = "entry-title")
        pageCtr += 1
        
        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            nLink = checkLink(i.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink:
                linkList.append([name,nLink])
    if len(linkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]

def bn_pcriskScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 0
    go = True
    link = "https://www.pcrisk.com/removal-guides"
    page = "?start="
    nLink = False
    print(f"{name} Started")
    while go:
        actualLink = link + page + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("div", class_ = "text-article")
        pageCtr += 10
        
        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            nLink = checkLink(i.p.text.replace("[.]", "."))
            
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
                
                
    if len(linkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]
        
def bn_adwareguruScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://adware.guru/category/removal-guide/page/"
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("p", class_ = "post-excerpt")
        pageCtr += 1
        
        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            nLink = checkLink(i.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink:
                linkList.append([name,nLink])
    if len(linkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]
        
def bn_myantispywareScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://www.myantispyware.com/categories/threats/adware/page/"
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("h3", class_ = "clearfix")
        pageCtr += 1

        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            nLink = checkLink(i.a.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink:
                linkList.append([name,nLink])
    if not linkList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]

def cyclonisSortByDate(dump):
    toBeSorted = []
    for i in range(6):
        text = (dump[i].text.split("\n"))
        toBeSorted.append(text[1])
        text = (dump[i+6].text.split("\n"))
        toBeSorted.append(text[1])
        text = (dump[i+12].text.split("\n"))
        toBeSorted.append(text[1])
    return (toBeSorted)   
def bn_cyclonisScrape(n, sharedVar, name, lastLink):
    PATH = Service("chromedriver.exe")
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = options, service=PATH)
    
    global lastLinksJSON
    newLinkList = []
    pageCtr = 1
    lastPage = 0 
    go = True 
    print(f"{name} Started")
    link = "https://www.cyclonis.com/threats/browser-hijacker"
    driver.get(link)
    time.sleep(2)
    dump = driver.find_elements(By.XPATH, "//div[@class='flex']")    
    
    linkList = cyclonisSortByDate(dump)

    for i in linkList:
        scamLink = checkLink(i)
        if scamLink:
            if scamLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            else:
                newLinkList.append([name,scamLink])
    
    pageCtr += 1
    
    link = "https://www.cyclonis.com/threats/browser-hijacker/page/"
    
    while go:
        actualLink = link + str(pageCtr)
        driver.get(actualLink)
        time.sleep(2)
        dump = driver.find_elements(By.XPATH, "//div[@class='flex']")
        
        linkList = cyclonisSortByDate(dump)
        
        for i in linkList:
            
            scamLink = checkLink(i)
            if scamLink:
                if scamLink == lastLink:
                    lastPage = pageCtr
                    go = False
                    break
                else:
                    newLinkList.append([name,scamLink])
        pageCtr+=1
    if len(newLinkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(newLinkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, newLinkList, newLinkList[0][1]]

class bn_howtofixguideDataScraper (threading.Thread):
    def __init__(self, link):
        threading.Thread.__init__(self)
        self.link = link
        self.ctr = 0
    def run(self):
        global sharedList
        global link_ctr_lock
        global linkCtr
        
        link_ctr_lock.acquire()
        self.ctr = linkCtr
        linkCtr += 1
        link_ctr_lock.release()
        
        htmlDump = requests.get(self.link)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        link = html.find("div", class_="su-table su-table-alternate su-table-fixed")
        
        data = checkLink(link.table.tr.strong.text)
        if data:
            data = data
            #append gathered data to global list
            shared_resource_lock.acquire()
            sharedList.append((self.ctr, data))
            shared_resource_lock.release()
            
def bn_howtofixguideDropLinks(list, lastLink):
    temp = []
    for i in list:
        if i[1]:
            temp.append(i[1])
    temp2 = []
    for i in temp:
        if i == lastLink:
            return temp2
        temp2.append(i)
    return temp2
def bn_howtofixguideProcessPage(linkTable, lastLink):
    global nLastLink
    threads = []
    go = True
    for i in range (len(linkTable)):
        tempLink = linkTable[i].a['href']
        curActulalLink = linkTable[i]
        if nLastLink == "":
            nLastLink = curActulalLink
        if curActulalLink == lastLink:
            go = False
            break
        thread = bn_howtofixguideDataScraper(tempLink)
        thread.start()
        threads.append(thread)
    for i in threads:
        i.join()
    return go  
def bn_howtofixguideScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    print(f"{name} Started")
    global sharedList 
    pageCtr = 0
    go = True
    link = "https://howtofix.guide/category/threat-encyclopedia/adware"
    page = "/page/"
    while go:
        actualLink = link + page + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("h2", "entry-title")
        
        if len(linkTable) == 0:
            break
        
        go = bn_howtofixguideProcessPage(linkTable, lastLink)
        pageCtr += 1
        if lastLink in sharedList:
            break
        go = False
    
    lst = len(sharedList)
    for i in range(0, lst):
        for j in range(0, lst-i-1):
            if (sharedList[j][0] > sharedList[j + 1][0]):
                temp = sharedList[j]
                sharedList[j]= sharedList[j + 1]
                sharedList[j + 1]= temp
    sharedList = bn_howtofixguideDropLinks(sharedList, lastLink)
    
    nSharedList = []
    for i in sharedList:
        nSharedList.append([name, i]) 
        
    if not nSharedList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(sharedList)} New Link(s) from {pageCtr} page(s)")
        
        sharedVar[n] = [name, nSharedList, nSharedList[0][1]]

def bn_regrunreanimatorScrape(n, sharedVar, name, lastDate):
    global lastLinksJSON
    newLinkList = []
    pageCtr = 1
    lastPage = 0 
    go = True
    print(f"{name} Started")
    link = "https://regrunreanimator.com/newvirus/category/guide-how-to/page/"
    while go:
        actualLink = link + str(pageCtr)
        res = requests.get(actualLink)
        html = BeautifulSoup(res.text,"lxml")
        linkTable = html.find_all("article")
        nLastDate = linkTable[0].header.div.a["title"]
        
        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            scamLink = i.header.h1.text
            scamDate = i.header.div.a["title"]
            scamLink = checkLink(scamLink)
            if scamLink:
                if scamDate == lastDate:
                    lastPage = pageCtr
                    go = False
                    break
                else:
                    newLinkList.append([name,scamLink])
        pageCtr += 1
    if len(newLinkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(newLinkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, newLinkList, nLastDate]

def bn_malwareguideScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://malware.guide/category/adware/page/"
    nLink = False
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("h2", "entry-title")
        
        if len(linkTable) == 0:
            break
            
        for i in linkTable:
            nLink = checkLink(i.a.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
        pageCtr+=1
    if not linkList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]

def bn_howtomalwareScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://howtomalware.com/category/adware/page/"
    nLink = False
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("a", "frontlist")
        pageCtr += 1
        
        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            nLink = checkLink(i.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
                
    if not linkList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]

def bn_2spywareScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    print(f"{name} Started")
    linkList = []
    go = True
    pageCtr = 1
    link = "https://www.2-spyware.com/c/viruses/adware"
    htmlDump = requests.get(link)
    html = BeautifulSoup(htmlDump.text, 'lxml')
    linkTable = html.find_all("div", "post news_post_3 news_post_3_bullet")
    
    if len(linkTable) != 0:
        for i in linkTable: 
            nLink = checkLink(i.h2.a.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink:
                linkList.append((name, nLink))
        pageCtr+=1
        page = "/page/"
        nLink = False
    else:
        go = False
        
        
    while go:
        actualLink = link + page + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find("div", {'class':'news-list-common'})
        linkTable = linkTable.find_all('h2')
        
        if len(linkTable) == 0:
            break
        
        for i in linkTable:
            nLink = checkLink(i.a.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
        pageCtr += 1
    if not linkList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]
        
def bn_greatisScrape(n, sharedVar, name, lastLink):
    PATH = Service("chromedriver.exe")
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = options, service=PATH)
    
    global lastLinksJSON
    newLinkList = []
    pageCtr = 1
    lastPage = 0 
    go = True
    print(f"{name} Started")
    link = "https://greatis.com/unhackme/help/page/"
    while go:
        actualLink = link + str(pageCtr)
        driver.get(actualLink)
        linkList = driver.find_elements(By.XPATH, "//div[@class='card-content']/div/header/h3/a")
        for i in linkList:
            scamLink = checkLink(i.text)
            
            if scamLink:
                if scamLink == lastLink:
                    lastPage = pageCtr
                    go = False
                    break
                else:
                    newLinkList.append([name,scamLink])
        pageCtr+=1
    if len(newLinkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(newLinkList)} New Link(s) from {lastPage} page(s)")
        
        # sharedVar[n] = [name, linkList, linkList[0][1]]

def bn_trojankillerScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    go = True
    pageCtr = 1
    link = "https://trojan-killer.net/category/removal/page/"
    nLink = False
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("span", {'class':'screen-reader-text'})
        
        if len(linkTable) == 0:
            break
        
        pageCtr += 1
        for i in linkTable:
            nLink = checkLink(i.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
                
    if not linkList:
            print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]

def bn_virusremovalinfoScrape (n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    go = True
    pageCtr = 1
    link = "https://virus-removal.info/page/"
    searchString = "/?s=pop+ups"
    nLink = False
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr) + searchString
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("h2", {'class':'post-title'})
        
        if len(linkTable) == 0:
            break
            
        pageCtr += 1
        for i in linkTable:
            nLink = checkLink(i.a.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
    if not linkList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]

def bn_cleanupallthreatsScrape(n, sharedVar, name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://cleanupallthreats.com/page/"
    nLink = False
    
    print(f"{name} Started")
    while go:
        
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, "lxml")
        linkTable = html.find_all("div", "entry-content")
        pageCtr += 1
        
        if len(linkTable) == 0:
            break
            
        for i in linkTable:
            nLink = checkLink(i.h2.a.text)
            if nLink == lastLink:
                lastPage = pageCtr
                go = False
                break
            if nLink and nLink not in linkList:
                linkList.append([name,nLink])
    if not linkList:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(linkList)} New Link(s) from {lastPage} page(s)")
        sharedVar[n] = [name, linkList, linkList[0][1]]
        



funcList = [        bn_malwaretipsScrape,        
                    bn_computipsScrape, 
                    bn_pcriskScrape, 
                    bn_adwareguruScrape, 
                    bn_myantispywareScrape,
                    bn_cyclonisScrape,
                    bn_howtofixguideScrape, 
                    bn_regrunreanimatorScrape, 
                    bn_malwareguideScrape, 
                    bn_howtomalwareScrape, 
                    bn_2spywareScrape,
                    bn_greatisScrape,
                    bn_trojankillerScrape,
                    bn_virusremovalinfoScrape,
                    bn_cleanupallthreatsScrape
                ]

def sortData (data):
    pass

def main():
    global lastLinksJSON
    global global_list
    
    lastLinksJSON = getLastLink()
    manager = multiprocessing.Manager()
    sharedVar = manager.dict()
    ctr = 0
    # print(lastLinksJSON["bn_pcrisk"])
    # thread = multiprocessing.Process(target = bn_pcriskScrape, args = (0, sharedVar, "bn_pcrisk", lastLinksJSON["bn_pcrisk"]))
    # thread.start()
    # thread.join()

    threads = []
    ctr = 0
    for key in lastLinksJSON:
        thread = multiprocessing.Process(target = funcList[ctr], args=(ctr, sharedVar, key, lastLinksJSON[key]))
        threads.append(thread)
        ctr+=1
    
    for i in threads:
        i.start()
    
    for i in threads:
        i.join()
    
    data = sharedVar.values()
    data.reverse()
    sourceList = [ "bn_malwaretips",		
                    "bn_computips",		
                    "bn_pcrisk",			
                    "bn_adwareguru",		
                    "bn_myantispyware",	
                    "bn_cyclonis",			
                    "bn_howtofixguide",	
                    "bn_regrunreanimator",	
                    "bn_malwareguide",		
                    "bn_howtomalware",		
                    "bn_2spyware",
                    "bn_greatis",			
                    "bn_trojankiller",			
                    "bn_virusremovalinfo",	
                    "bn_cleanupallthreats"]
    
    dataDict = {
        
    }
    
    memory = []
    
    for i in data:
        
        dataDict.update({i[0] : [i[1], i[2]]})
        memory.append(i[0])
        # print("name: " + i[0])
        # print(f"linkList: {i[1]}")
        # print("lastLink: " + i[2])
    print("\n")
    for i in sourceList:
        try:
            saveToCache(i, dataDict[i][0], dataDict[i][1])
        except:
            print(f"No new links from {i}")
            pass
    print("\n")
    saveData()
    
    print(f"\nTotal Links: {len(global_list)}")
    if os.path.exists("linksCountHistory.csv"):
        with open("linksCountHistory.csv", "a") as f:
            f.write(f"{datetime.date.today()}, {len(global_list)}\n")
    else:
        with open("linksCountHistory.csv", "w") as f:
            f.write(f"{datetime.date.today()}, Link(s): {len(global_list)} (Unfiltered)\n")
    
    
if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time() - start
    
    print(f"\nTime Elapsed: {end:.2f} seconds")

















