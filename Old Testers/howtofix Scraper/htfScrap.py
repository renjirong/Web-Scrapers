# ---------------------------------------------------------------------------------------------------------------------------------------------
# Code written and updated by 
# Renji David Ong (TR-PH-INTRN)
# Last Update: 08/25/22 12:00AM
# ---------------------------------------------------------------------------------------------------------------------------------------------
import requests 
import re
from bs4 import BeautifulSoup
import os
import time
import pandas as pd
import datetime
import os
import threading 

#global var
sharedList = []
nLastLink = ""
linkCtr = 0


#Global variable locks
shared_resource_lock=threading.Lock()
link_ctr_lock = threading.Lock()

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



def noLink():
    print("There is currently no existing 'lastLink.txt' or the link is invalid do you wish to proceed?")
    proceed = input("Do you wish to proceed? Y/N ")
    print(proceed != "Y" and proceed != "y")
    if proceed != "Y" and proceed != "y":
        exit("Quitting Program...")
    else:
        return input("Enter last known 'URL': " )
def saveData(data, nLastLink):
    print(f"\nScraped Links: {len(data)}")
    df = pd.DataFrame(data)
    csvFormat = df.to_csv(header= "",index=False)
    print(f"\nNew Last Link: {nLastLink}")
    
    try:
        with open("lastLink.txt", "w") as f:
            f.write(nLastLink)
        print("Last Link Saved in: lastLink.txt\n")
    except Exception as e:
        print(e)
        name = str(datetime.datetime.now()).replace(":", "-").split(".")
        name = name[0] + "-" + name[1][:4]
        name = name.replace("-", "").replace(" ", "") + "out.csv"
        print("Last Link Retrieved Saved in: " + name + "\n")
        with open("lastLink.txt", "w") as f:
            f.write(nLastLink)
            
    try:
        print("Saving...")
        with open("out.csv", "w") as f:
            csvFormat = csvFormat.split("\n")
            for i in csvFormat:
                f.write(i)
                
        print("Saved!")
        print("New File Name: out.csv")
    except Exception as e:
        print(e)
        
        print("Trying Again...")
        name = str(datetime.datetime.now()).replace(":", "-").split(".")
        name = name[0] + "-" + name[1][:4]
        name = name.replace("-", "").replace(" ", "") + "out.csv"
        
        with open(name, "w") as f:
            for i in csvFormat.split("\n"):
                f.writelines(i)
        print("Saved!")
        print("New File Name: "+name)
    except Exception as e:
        print(e)       
def getLastLink():
    try:
        if os.stat("lastLink.txt").st_size == 0:
            return noLink()
            
        with open("lastLink.txt", "r") as f:
            link = f.readline()
            if checkLink(link) == link:
                return link
            else:
                return noLink()
            
    except Exception as e:
        with open("lastLink.txt", "w") as f:
            f.write("")
        return noLink()

def dropLinks(list, lastLink):
    
    temp = []
    for i in list:
        if i[1]:
            temp.append(i[1])
        
        
    print(lastLink)
    for i in range(len(temp)):
        if temp[i] == lastLink:
            return temp[:i]
    return temp
        
    
class dataScraper (threading.Thread):
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

def processPage(linkTable, lastLink):
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
        thread = dataScraper(tempLink)
        thread.start()
        threads.append(thread)
        
    for i in threads:
        i.join()
    return go  

def main():
    global sharedList 
    lastLink = getLastLink()
    pageCtr = 0
    go = True
    link = "https://howtofix.guide/category/threat-encyclopedia/adware"
    page = "/page/"
    while go:
        actualLink = link + page + str(pageCtr)
        print("Processing page: " + str(pageCtr))
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("h2", "entry-title")
        go = processPage(linkTable, lastLink)
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
                
    
        
    sharedList = dropLinks(sharedList, lastLink)

    if len(sharedList):
        print("\nLast Link: " + lastLink)
        saveData(sharedList, sharedList[0])
    else:
        print("No new Links")

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time() - start
    
    print(f"\nTime Elapsed: {end:.2f} seconds")




    