from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
import csv
import threading

lock = threading.Lock()

def bs_webpage(url, parser):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})  # make req disguised as Firefox request (403 otherwise)
    webpage = urlopen(req).read()  # read response (html doc)
    return BeautifulSoup(webpage, parser)  # make it parse-able for bs

def scan_entry(entry):
    authors = ""
    alt_titles = ""

    url = entry.find('a')['href']  # get manga link
    print(url)
    soup = bs_webpage(url, 'lxml')

    title = soup.find('div', attrs={'class': "w-title"}).text.strip()  # strip removes whitespace on front and end
    for label in soup.select('td > label'):
        if label.string.strip() == "Author:":
            for item in label.findParent().find_all('a'):  # go back to parent td and get all <a tags
                if item.text.strip() != "":  # author exists (even when author dne, there is still a <a)
                    if authors == "":
                        authors = item.text.strip()
                    else:
                        authors += "\n" + item.text.strip()
        elif label.string.strip() == "Alternative:":
            item = label.next_sibling
            if item is not None:  # might say "None" or just be blank
                item = item.text.strip()
                if item != "None":  # todo: fix whitespace inbtwn (https://www.mangago.me/read-manga/the_evil_empress_loves_me_so_much/)
                    alt_titles = item
            break
    return title, authors, alt_titles

def write_entry(writer, entry, url):
    title, authors, alt_titles = scan_entry(entry)
    lock.acquire()
    try:
        writer.writerow([title, url, authors, alt_titles])
    finally:
        lock.release()


start_time = time.time()

init_run = True
max_page = 1
page_no = 1
file = open('test.csv', 'w')
writer = csv.writer(file)
writer.writerow(['TITLE', 'LINK', 'AUTHOR(S)', 'ALT-TITLE(S)'])

while page_no <= max_page:
    url = f"https://www.mangago.me/home/people/29556/manga/1/?page={page_no}"  # todo: 1 = want, 2 = reading, 3 = read
    page_no += 1
    soup = bs_webpage(url, 'lxml')  # lxml is faster

    # find max # of pages
    if init_run:
        init_run = False
        option = soup.select('li > span > select > option')  # collect all page #s
        max_page = int(option[len(option) - 1].text.strip())  # get the last page #

    # traverse every manga in list
    threads = []
    for entry in soup.findAll("h3", attrs={'class': 'title'}):  # entries w/ <h3 class=title #todo: threads!
        threads.append(threading.Thread(target=write_entry, args=(writer, entry, url)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
file.close()
end_time = time.time()
elapsed_time = end_time - start_time
print(elapsed_time)
