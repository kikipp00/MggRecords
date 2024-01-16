from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
import csv
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

lock = threading.Lock()

def bs_webpage(url, parser):
    # Function to fetch webpage content using a given URL and parser
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, parser)

def scan_entry(entry): #same, unchanged
    authors = ""
    alt_titles = ""
    url = entry.find('a')['href']  # get manga link
    #print(url)
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
    # Function to write manga entry information to a CSV file
    title, authors, alt_titles = scan_entry(entry)
    with lock:
        writer.writerow([title, url, authors, alt_titles])

def scrape_page(url, writer):
    # Function to scrape a page of manga entries
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    session = requests.Session()
    session.headers.update(headers)

    global init_run  # global variable
    soup = bs_webpage(url, 'lxml')

    # Find max #
    if init_run:
        init_run = False
        option = soup.select('li > span > select > option')
        if len(option) > 0:
            max_page = int(option[len(option) - 1].text.strip())

    # Collect entry/urls
    threads = []
    for entry in soup.findAll("h3", attrs={'class': 'title'}):
        threads.append((entry, url))

    # Use threadpool scraping
    with ThreadPoolExecutor(max_workers=5) as executor: #becareful of worker add a sleep if needed
        for entry, url in threads:
            executor.submit(write_entry, writer, entry, url)

def main():
    # Main function to initiate the scraping process
    global init_run
    init_run = True
    max_page = 1
    page_no = 1

    start_time = time.time()

    # better practice
    with open('test.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['TITLE', 'LINK', 'AUTHOR(S)', 'ALT-TITLE(S)'])

        # Loop through pages and scrape each one
        while page_no <= max_page:
            url = f"https://www.mangago.me/home/people/29556/manga/1/?page={page_no}"
            page_no += 1
            scrape_page(url, writer)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")

if __name__ == "__main__":
    main()