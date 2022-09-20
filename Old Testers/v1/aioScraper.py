# ---------------------------------------------------------------------------------------------------------------------------------------------
# Code written and updated by 
# Renji David Ong (TR-PH-INTRN) & Junard Febrer (TR-PH-INTRN)
# Last Update: 09/05/22 11:40PM
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
    if temp:
        if ".exe" not in temp:
            return verifyLink(String)
    else:
        return False
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
        with open("lastLinks.json", "w") as f:
            f.write(json.dumps(lastLinksJSON))
        print("Last Link JSON Saved in: lastLink.json\n")
    except Exception as e:
        print(e)
        name = str(datetime.datetime.now()).replace(":", "-").split(".")
        name = name[0] + "-" + name[1][:4]
        name = name.replace("-", "").replace(" ", "") + "out.csv"
        print("Last Link Retrieved Saved in: " + name + "\n")
        with open("lastLink.json", "w") as f:
            f.write(nLastLink)
            
    try:
        print("Saving...")
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
            with open("out.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(global_list)
            print("Saved!")
            print("New File Name: "+name)
        else:
            print("Nothing new to save")
    except Exception as e:
        print(e)     

def saveToCache(name, data, nLastLink):
    global global_list
    global lastLinksJSON
    
    global_resource_lock.acquire()
    global_list += data
    lastLinksJSON[name] = nLastLink
    global_resource_lock.release() 
def getLastLink():
    global lastLinksJSON
    try:
        with open("lastLinks.json") as f:
            lastLinksJSON = json.load(f)
    except Exception as e:
        print(e) 

def bn_malwaretipsScrape(driver, name, lastLink):
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
            scamLink = verifyLink(i.text)
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
        saveToCache(name, newLinkList, newLinkList[0][1])

def bn_computipsScrape(name, lastLink):
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
        saveToCache(name, linkList, linkList[0][1])

def bn_pcriskScrape(name, lastLink):
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
        
        for i in linkTable:
            nLink = verifyLink(i.p.text.replace("[.]", "."))
            
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
        saveToCache(name, linkList, linkList[0][1])
        
def bn_adwareguruScrape(name, lastLink):
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
        saveToCache(name, linkList, linkList[0][1])
        
def bn_myantispywareScrape(name, lastLink):
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
        saveToCache(name, linkList, linkList[0][1])

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
    
def bn_cyclonisScrape(driver, name, lastLink):
    global lastLinksJSON
    newLinkList = []
    pageCtr = 1
    lastPage = 0 
    go = True 
    print(f"{name} Started")
    link = "https://www.cyclonis.com/threats/browser-hijacker"
    driver.get(link)
    time.sleep(3)
    dump = driver.find_elements(By.XPATH, "//div[@class='flex']")    
    
    linkList = cyclonisSortByDate(dump)

    for i in linkList:
        scamLink = verifyLink(i)
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
        dump = driver.find_elements(By.XPATH, "//div[@class='flex']")
        
        linkList = cyclonisSortByDate(dump)
        
        for i in linkList:
            scamLink = verifyLink(i)
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
        saveToCache(name, newLinkList, newLinkList[0][1])

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
        if i == lastLink[1]:
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
def bn_howtofixguideScrape(name, lastLink):
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
        saveToCache(name, nSharedList, nSharedList[0])

def bn_regrunreanimatorScrape(name, lastDate):
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
        list = html.find_all("article")
        nLastDate = list[0].header.div.a["title"]
        for i in list:
            scamLink = i.header.h1.text
            scamDate = i.header.div.a["title"]
            scamLink = verifyLink(scamLink)
            if scamLink:
                if scamDate == lastDate:
                    lastPage = pageCtr
                    go = False
                    break
                else:
                    newLinkList.append([name,scamLink])
        go=False
        
    if len(newLinkList) == 0:
        print(f"{name}: No new links")
    else:
        print(f"{name}: {len(newLinkList)} New Link(s) from {lastPage} page(s)")
        saveToCache(name, newLinkList, nLastDate)

def bn_malwareguideScrape(name, lastLink):
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
        saveToCache(name, linkList, linkList[0][1])

def bn_howtomalwareScrape(name, lastLink):
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
        saveToCache(name, linkList, linkList[0][1])

def bn_2spywareScrape(name, lastLink):
    global lastLinksJSON
    print(f"{name} Started")
    linkList = []
    go = True
    pageCtr = 1
    link = "https://www.2-spyware.com/c/viruses/adware"
    htmlDump = requests.get(link)
    html = BeautifulSoup(htmlDump.text, 'lxml')
    linkTable = html.find_all("div", "post news_post_3 news_post_3_bullet")
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
    while go:
        actualLink = link + page + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find("div", {'class':'news-list-common'})
        linkTable = linkTable.find_all('h2')
        
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
        saveToCache(name, linkList, linkList[0][1])
        
def bn_greatisScrape(driver, name, lastLink):
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
            scamLink = verifyLink(i.text)
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
        saveToCache(name, newLinkList, newLinkList[0][1])

def bn_trojankillerScrape(name, lastLink):
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
        linkTable = html.find_all("h2", {'class':'post-box-title'})
        
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
        saveToCache(name, linkList, linkList[0][1])

def bn_virusremovalinfoScrape (name, lastLink):
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
        saveToCache(name, linkList, linkList[0][1])

def bn_cleanupallthreats(name, lastLink):
    global lastLinksJSON
    linkList = []
    pageCtr = 1
    go = True
    link = "https://cleanupallthreats.com/page/"
    nLink = False
    html = requests.get(link)
    print(f"{name} Started")
    while go:
        actualLink = link + str(pageCtr)
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, "lxml")
        linkTable = html.find_all("div", "entry-content")
        pageCtr += 1
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
        saveToCache(name, linkList, linkList[0][1])

def main():
    global lastLinksJSON
    
    PATH = Service("chromedriver.exe")
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options = options, service=PATH) 
    getLastLink()
    
    threads = []
    thread = threading.Thread(bn_cleanupallthreats("bn_cleanupallthreats", lastLinksJSON["bn_cleanupallthreats"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_virusremovalinfoScrape("bn_virusremovalinfo", lastLinksJSON["bn_virusremovalinfo"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_trojankillerScrape("bn_trojankiller", lastLinksJSON["bn_trojankiller"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_greatisScrape(driver, "bn_greatis", lastLinksJSON["bn_greatis"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_2spywareScrape("bn_2spyware", lastLinksJSON["bn_2spyware"]))
    threads.append(thread)
    
    #LINK IS DOWN!!
    # thread = threading.Thread(bn_howtomalwareScrape("bn_howtomalware", lastLinksJSON["bn_howtomalware"]))
    # threads.append(thread)
    
    thread = threading.Thread(bn_malwareguideScrape("bn_malwareguide", lastLinksJSON["bn_malwareguide"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_regrunreanimatorScrape("bn_regrunreanimator", lastLinksJSON["bn_regrunreanimator"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_howtofixguideScrape("bn_howtofixguide", lastLinksJSON["bn_howtofixguide"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_cyclonisScrape(driver,"bn_cyclonis", lastLinksJSON["bn_cyclonis"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_myantispywareScrape("bn_myantispyware", lastLinksJSON["bn_myantispyware"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_adwareguruScrape("bn_adwareguru", lastLinksJSON["bn_adwareguru"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_pcriskScrape("bn_pcrisk", lastLinksJSON["bn_pcrisk"]))
    threads.append(thread)
    
    thread = threading.Thread(bn_computipsScrape("bn_computips", lastLinksJSON["bn_computips"]))
    threads.append(thread)
    
    thread = threading.Thread(target=bn_malwaretipsScrape(driver, "bn_malwaretips", lastLinksJSON["bn_malwaretips"]))
    threads.append(thread)
    
    for i in threads:
        i.start()
        i.join()
        
    print("Saving...")  
    saveData()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time() - start
    
    print(f"\nTime Elapsed: {end:.2f} seconds")

















