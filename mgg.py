from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
import csv
from concurrent.futures import ThreadPoolExecutor
import threading

# uncomment if ssl error
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

lock = threading.Lock()


def bs_webpage(url, parser):
    # Function to fetch webpage content using a given URL and parser
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, parser)


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
    return title, url, authors, alt_titles


def write_entry(writer, entry):
    title, url, authors, alt_titles = scan_entry(entry)
    with lock:
        writer.writerow([title, url, authors, alt_titles])


def main():
    start_time = time.time()
    init_run = True
    max_page = 1
    page_no = 1

    with open('test.csv', 'w', newline='') as file: # don't need to explicitly close bc "with"
        writer = csv.writer(file)
        writer.writerow(['TITLE', 'LINK', 'AUTHOR(S)', 'ALT-TITLE(S)'])

        # traverse all pages
        while page_no <= max_page:
            url = f"https://www.mangago.me/home/people/2560141/manga/1/?page={page_no}" # todo: 1 = want, 2 = reading, 3 = read
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
                    threads.append(executor.submit(write_entry, writer, entry))

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()
