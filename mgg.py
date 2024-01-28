from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import pandas as pd
import psycopg2
from configparser import ConfigParser

# uncomment if ssl error
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

lock = threading.Lock()
database = "mgg.db"


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


# create a database connection to a PostgreSQL database
def create_connection():
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
    except (Exception, psycopg2.DatabaseError) as e:
        print(e)
    return conn


# initialize db
def init_db():
    conn = create_connection()
    with conn:
        with open('schema.sql', 'r') as f:
            conn.cursor().execute(f.read())


# export PostgreSQL db to csv (category is str)
# pandas not made for Postgres
def to_csv(category):
    conn = create_connection()
    db_df = pd.read_sql_query(f"SELECT * FROM {category}", conn)
    db_df.to_csv(f"{category}.csv", index=False)
    return f"{category}.csv"


# bs parse page
def bs_webpage(url, parser):
    # Function to fetch webpage content using a given URL and parser
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=headers)
        webpage = urlopen(req).read()
    except Exception as e:
        print(e)
        return False
    return BeautifulSoup(webpage, parser)


# grab all info from entry
def scan_entry(entry):
    authors = []
    alt_titles = []
    url = entry.find('a')['href']  # get manga link
    # print(url)
    soup = bs_webpage(url, 'lxml')
    if not soup:  # stop if error
        return False

    title = soup.find('div', attrs={
        'class': "w-title"}).text.strip()  # strip removes whitespace on front and end #todo: remove (Yaoi)
    for label in soup.select('td > label'):
        if label.string.strip() == "Author:":
            for item in label.findParent().find_all('a'):  # go back to parent td and get all <a tags
                if item.text.strip() != "":  # author exists (even when author dne, there is still a <a)
                    authors.append(item.text.strip())
        elif label.string.strip() == "Alternative:":
            item = label.next_sibling
            if item is not None:  # might say "None" or just be blank
                item = item.text.strip()
                if item != "None":  # todo: fix whitespace inbtwn (https://www.mangago.me/read-manga/the_evil_empress_loves_me_so_much/)
                    alt_titles = [x.strip() for x in item.split(';')]
            break
    return title, url, authors, alt_titles


# insert entry to table
def insert_entry(entry, category, userid):
    title, url, authors, alt_titles = scan_entry(entry)
    if not title:  # (untested) manga no longer exists
        return False
    items = (userid, title, url, authors, alt_titles)
    with lock:
        conn = create_connection()
        with conn:
            cur = conn.cursor()
            if category == 1:
                cur.execute("INSERT INTO Want(userid, title, url, author, alt_title) VALUES %s", (items,))
            elif category == 2:
                cur.execute("INSERT INTO Reading(userid, title, url, author, alt_title) VALUES %s", (items,))
            else:
                cur.execute("INSERT INTO AlreadyRead(userid, title, url, author, alt_title) VALUES %s", (items,))
            conn.commit()
    return True


# grab all manga from category
def scan_category(category, userid):
    if userid == 1:  # special account for mgg
        return False
    init_run = True
    max_page = 1
    page_no = 1
    while page_no <= max_page:
        url = f"https://www.mangago.me/home/people/{userid}/manga/{category}/?page={page_no}"
        page_no += 1
        soup = bs_webpage(url, 'lxml')
        if not soup:  # stop if error
            return False

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
                threads.append(executor.submit(insert_entry, entry, category, userid))
    return True


def main():
    start_time = time.time()
    init_db()

    # traverse all categories
    for category in range(2, 4):  # 1: Want, 2: Reading, 3: Already Read
        if not scan_category(category, 3306689):
            print("invalid account")
            break

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Reading")
    rs = cur.fetchall()
    for row in rs:
        print(row)

    to_csv("Reading")


if __name__ == "__main__":
    main()
