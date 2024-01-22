from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import sqlite3
from sqlite3 import Error

# uncomment if ssl error
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

lock = threading.Lock()
database = "mgg.db"


# create a database connection to a SQLite database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


# initialize db
def init_db():
    conn = create_connection(database)
    with conn:
        with open('schema.sql') as f:
            conn.executescript(f.read())


# bs parse page
def bs_webpage(url, parser):
    # Function to fetch webpage content using a given URL and parser
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, parser)


# grab all info from entry
def scan_entry(entry):
    authors = ""
    alt_titles = ""
    url = entry.find('a')['href']  # get manga link
    print(url)
    soup = bs_webpage(url, 'lxml')

    title = soup.find('div', attrs={
        'class': "w-title"}).text.strip()  # strip removes whitespace on front and end #todo: remove (Yaoi)
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
                if item != "None":  #todo: fix whitespace inbtwn (https://www.mangago.me/read-manga/the_evil_empress_loves_me_so_much/)
                    alt_titles = item
            break
    return title, url, authors, alt_titles


# insert entry to table
def insert_entry(entry, category):
    title, url, authors, alt_titles = scan_entry(entry)
    items = (title, url, authors, alt_titles)
    with lock:
        conn = create_connection(database)
        with conn:
            cur = conn.cursor()
            if category == 1:
                cur.execute("INSERT INTO Want(title, url, author, alt_title) VALUES (?,?,?,?)", items)
            elif category == 2:
                cur.execute("INSERT INTO Reading(title, url, author, alt_title) VALUES (?,?,?,?)", items)
            else:
                cur.execute("INSERT INTO AlreadyRead(title, url, author, alt_title) VALUES (?,?,?,?)", items)
            conn.commit()


# grab all manga from category
def scan_category(category, userid):
    init_run = True
    max_page = 1
    page_no = 1
    while page_no <= max_page:
        url = f"https://www.mangago.me/home/people/{userid}/manga/{category}/?page={page_no}"
        page_no += 1
        soup = bs_webpage(url, 'lxml')

        # find max # of pages
        if init_run:
            init_run = False
            option = soup.select('li > span > select > option')
            if len(option) > 0:
                max_page = int(option[len(option) - 1].text.strip())

        # traverse every manga in list
        with ThreadPoolExecutor(max_workers=10) as executor:
            threads = []
            for entry in soup.findAll("h3", attrs={'class': 'title'}):
                threads.append(executor.submit(insert_entry, entry, category))


def main():
    start_time = time.time()
    init_db()

    # traverse all categories
    for category in range(1, 4):  # 1: Want, 2: Reading, 3: Already Read
        scan_category(category, "3306689")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()
