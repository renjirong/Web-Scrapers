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


def main():
    
    lastLink = getLastLink()
    linkList = []
    pageCtr = 0
    go = True
    link = "https://www.pcrisk.com/removal-guides"
    page = "?start="
    nLink = False
    while go:
        actualLink = link + page + str(pageCtr)
        print("Processing page: " + str(pageCtr))
        
        htmlDump = requests.get(actualLink)
        html = BeautifulSoup(htmlDump.text, 'lxml')
        linkTable = html.find_all("div", class_ = "text-article")
        pageCtr += 10
        
        for i in linkTable:
            textList = i.p.text.replace("[.]", ".").strip().split(" ")
            
            print(verifyLink(i.p.text.replace("[.]", ".")))
            for j in textList:
                temp = checkLink(j)
                if temp:
                    nLink = j
                    break 
            
            if nLink == lastLink:
                go = False
                break
            if nLink and nLink not in linkList:
                print(nLink)
                linkList.append(nLink)
            
    if len(linkList):
        saveData(linkList, linkList[0])
    else:
        print("No New Links")
        

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time() - start
    
    print(f"\nTime Elapsed: {end:.2f} seconds")




    