import datetime
from os import makedirs, chdir
import re
import string
import sys
import requests
import bs4
from bs4 import Tag

LINK_PREFIX = 'http://www.sporthoj.com'
IMG_URL = 'http://www.sporthoj.com/galleri/bild?id={0}&header=1'

post_monolith = []


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


def download_images(post: Tag) -> None:
    image_links = [LINK_PREFIX + link.attrs.get('href') for link in post.find_all(href=re.compile('/galleri/visabild'))]
    for url in image_links:
        image_id = re.search(r'id=([0-9]+)[&]', url).group(1)
        print('    Downloading image: ' + IMG_URL.format(image_id))
        r = requests.get(IMG_URL.format(image_id), stream=True)
        with open(image_id + '.jpg', 'wb') as fd:
            for chunk in r.iter_content(128):
                fd.write(chunk)


def grab_post_datetime(post: Tag) -> string:
    time_text = post.find(id='publicerad').text
    date_time_string = re.search(r'Tidpunkt:(.+)[|]', time_text).group(1).strip()
    post_datetime = datetime.datetime.strptime(date_time_string, '%d / %m - %Y %H:%M').strftime('%y-%m-%d_%H:%M')
    return post_datetime


def clean_filename(name: string) -> string:
    trans = str.maketrans(string.whitespace, '_' * len(string.whitespace), '/\\.?*%:|"><')
    return name.translate(trans)


def fetch_all_data(post: Tag):
    title = post.find(style='font-size: 18px').text
    post_datetime = grab_post_datetime(post)
    file_name = clean_filename(post_datetime + '-' + title)
    print('  Creating folder: ' + file_name)
    makedirs(file_name)
    chdir(file_name)
    download_images(post)
    text = post.find(style='font-size: 13px').text
    print('    Saving post text')
    with open('post_text.txt', 'w+', encoding='utf-8') as post_text_file:
        post_text_file.write(text)
    chdir('..')
    post_monolith.append((post_datetime, title + '\n' + text + '\n\n'))


def fetch_all_blog_posts(url: string):
    page = requests.get(url)
    full_soup = bs4.BeautifulSoup(page.text)
    blog_title = full_soup.find(style='font-size: 26px').text
    file_name = clean_filename(blog_title)
    print('Creating folder: ' + file_name)
    makedirs(file_name)
    chdir(file_name)
    for post in full_soup.find_all(id='inlagg')[0].children:
        fetch_all_data(post)
    chdir('..')


def main(argv):
    print("Scraping all blog entries from: " + argv[0])
    blog_urls = get_all_blog_urls(argv[0])
    print("Will read these urls: ")
    for url in blog_urls:
        print("  " + url)

    for url in blog_urls:
        print('Fetching: ' + url)
        fetch_all_blog_posts(url)

    print('Saving all posts to monolith. ')
    post_monolith.sort(key=lambda item: item[0])
    with open('post_monolith.txt', 'w+', encoding='utf-8') as post_monolith_file:
        for date_time, text in post_monolith:
            post_monolith_file.write(date_time + ' - ' + text)


if __name__ == "__main__":
    main(sys.argv[1:])