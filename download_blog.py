import datetime
import re
import string
import sys
import requests
import bs4
from twisted.web.resource import Resource

LINK_PREFIX = 'http://www.sporthoj.com'

post_links = []


def fetch_all_post_urls(url: string) -> []:
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text)
    hrefs = soup.find_all(id='inlagg')[1].find_all(href=True)
    post_links.extend([LINK_PREFIX + href.attrs.get('href') for href in hrefs])
    return [href.attrs.get('href') for href in hrefs]


def get_all_blog_urls(url: string) -> []:
    blog_urls = [url, ]
    initial_page = requests.get(url)
    initial_soup = bs4.BeautifulSoup(initial_page.text)
    post_link = initial_soup.find_all(id='inlagg')[1].find_all(href=True)[0].attrs.get('href')
    page = requests.get(LINK_PREFIX + post_link)
    soup = bs4.BeautifulSoup(page.text)
    hrefs = soup.find_all(id='garage')[0].find_all(href=True)
    blog_urls.extend([LINK_PREFIX + href.attrs.get('href') for href in hrefs])
    return blog_urls


def fetch_all_data(post: Resource):
    title = post.find(style='font-size: 18px').text
    image_links = [LINK_PREFIX + link.attrs.get('href') for link in post.find_all(href=re.compile('/galleri/visabild'))]
    text = post.find(style='font-size: 13px').text
    time_text = post.find(id='publicerad').text
    date_time_string = re.search(r'Tidpunkt:(.+)[|]', time_text).group(1).strip()
    post_datetime = datetime.datetime.strptime(date_time_string, '%d / %m - %Y %H:%M').strftime('%y-%m-%d_%H:%M')


def fetch_all_blog_posts(url: string):
    page = requests.get(url)
    full_soup = bs4.BeautifulSoup(page.text)
    for post in full_soup.find_all(id='inlagg')[0].children:
        fetch_all_data(post)





def main(argv):
    print("Scraping all blog entries from: " + argv[0])
    blog_urls = get_all_blog_urls(argv[0])
    print("Will read these urls: ")
    for url in blog_urls:
        print("  " + url)

    for url in blog_urls:
        fetch_all_blog_posts(url)


if __name__ == "__main__":
    main(sys.argv[1:])