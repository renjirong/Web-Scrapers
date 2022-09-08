import re

def checkLink(string):
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


with open("lastLink.txt","r") as i:
    link = "Remove Cpaoffers.network Ads"
    link = link.strip().split(" ")
    
    for i in  link:
        print(checkLink(i))

