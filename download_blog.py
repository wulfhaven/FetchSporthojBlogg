import string
import sys
import requests
import bs4

__author__ = 'ulvhamne'

post_links = []


def fetch_all_post_urls(url: string) -> []:
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text)
    hrefs = soup.find_all(id='inlagg')[1].find_all(href=True)
    post_links.extend([href.attrs.get('href') for href in hrefs])
    return [href.attrs.get('href') for href in hrefs]


def fetch_all_blog_urls(url: string) -> []:
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text)
    post_link = soup.find_all(id='inlagg')[1].find_all(href=True)[0].attrs.get('href')
    requests.get(post_link)

    return list


def main(argv):
    print("Scraping all blog entries from: " + argv[0])

    post_links.extend(fetch_all_post_urls(argv[0]))


if __name__ == "__main__":
    main(sys.argv[1:])