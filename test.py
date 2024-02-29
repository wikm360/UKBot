def getlink(text) :
    import requests
    from bs4 import BeautifulSoup as BS
    import re
    def not_lacie(href):
        return href and not re.compile("lacie").search(href)

    final = []
    url = text
    r = requests.get(url)
    content = r.text
    soup = BS(content,'html.parser')
    elem = list(soup.find_all(href=not_lacie))
    count = len(elem)
    for i in range(0,count) :
        li = str(elem[i]).split(" ")
        count2 = len(li)
        for j in range(0,count2) : 
            if "href" in li[j] :
                links = str(li[j]).split("=")
                count3 = len(links)
                for z in range(0,count3) :
                    if str(text).split("//")[1] in links[z] :
                        string = links[z]
                        final.append(string)
                        # print(type(final))
                        # print(final)

    return final

links=getlink("https://wikm.ir")
count = len(links)
for i in range (0,count) :
    print(links[i])
#getlink("https://soft98.ir")
