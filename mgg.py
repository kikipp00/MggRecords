from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

#for pageno in range(1, 1):
    #website = f"https://www.mangago.me/home/people/29556/manga/?page={pageno}/"
url = f"https://www.mangago.me/home/people/29556/manga/1/"
response = Request(url, headers={'User-Agent': 'Mozilla]5.0'}) #make req disguised as Firefox request (403 otherwise)
webpage = urlopen(response).read() #read response (html doc)
soup = BeautifulSoup(webpage, 'html.parser') #make it parse-able for bs

for entry in soup.findAll("h3", attrs={'class': 'title'}): #entries w/ <h3 class=title
    url = entry.find('a')['href'] #get link
    print(url)
    response = Request(url, headers={'User-Agent': 'Mozilla]5.0'})
    webpage = urlopen(response).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    title = soup.find('div', attrs={'class': "w-title"})
    print(title.text.strip()) #strip removes whitespace
    for label in soup.select('td > label'):
        if label.string.strip() == "Author:":
            for author in label.findParent().find_all('a'): #go back to parent td and get all <a tags
                print(author.text.strip())
        elif label.string.strip() == "Alternative:":
            if label.next_sibling is not None:
                print(label.next_sibling.text.strip()) #todo: fix whitespace inbetween (https://www.mangago.me/read-manga/the_evil_empress_loves_me_so_much/)
                break





"""anchor_tags = soup.find_all('a')
href_links = [a.get('href') for a in anchor_tags if a.get('href') and a.get('href').startswith('https://www.mangago.me/read-manga/')]
print(href_links)
for manga in set(href_links):
    website = manga
    req = Request(website, headers={'User-Agent': 'Mozilla]5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "lxml")
    box = soup.find(class_="w-title")
    if box is not None:
        title = box.get_text()
        at = soup.find("label",text= lambda t: 'Alternative' in t)
        for i in at:
            print(i.get_text())
        #print(at)"""








