from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time


def bs_webpage(url, parser):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})  # make req disguised as Firefox request (403 otherwise)
    webpage = urlopen(req).read()  # read response (html doc)
    return BeautifulSoup(webpage, parser)  # make it parse-able for bs


start_time = time.time()

init_run = True
max_page = 1
page_no = 1
while page_no < max_page or page_no == max_page:
    url = f"https://www.mangago.me/home/people/29556/manga/1/?page={page_no}"  # todo: 1 = want, 2 = reading, 3 = read
    page_no += 1
    soup = bs_webpage(url, 'lxml')  # lxml is faster

    # find max # of pages
    if init_run:
        init_run = False
        lines = soup.select('li > span > select > option')  # collect all page #s
        max_page = int(lines[len(lines) - 1].text.strip())  # get the last page #

    # traverse every manga in list
    for entry in soup.findAll("h3", attrs={'class': 'title'}):  # entries w/ <h3 class=title #todo: threads!
        url = entry.find('a')['href']  # get link
        print(url)
        soup = bs_webpage(url, 'lxml')

        title = soup.find('div', attrs={'class': "w-title"})
        print(title.text.strip())  # strip removes whitespace on front and end
        for label in soup.select('td > label'):
            if label.string.strip() == "Author:":
                print("Author: ")
                for author in label.findParent().find_all('a'):  # go back to parent td and get all <a tags
                    if author.text.strip() != "":  # since even when author dne, there is still a <a
                        print(author.text.strip())
            elif label.string.strip() == "Alternative:":
                print("Alternative: ")
                if label.next_sibling is not None:  # supposedly, should say "None" if no alt-titles available
                    print(
                        label.next_sibling.text.strip())  # todo: fix whitespace inbetween (https://www.mangago.me/read-manga/the_evil_empress_loves_me_so_much/)
                    break

end_time = time.time()
elapsed_time = end_time - start_time
print(elapsed_time)
