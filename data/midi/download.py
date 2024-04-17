import os

import requests
from lxml import html

URL = "https://www.vgmusic.com/music/console/"


def main(start_url: str) -> None:
    page = requests.get(start_url)
    webpage = html.fromstring(page.content)
    links = webpage.xpath("//a/@href")
    files = list()
    for link in links:
        if link[0].isalpha():
            follow_link(start_url, link)


def follow_link(base: str, new_link: str) -> None:
    new_base = base + new_link
    page = requests.get(new_base)
    webpage = html.fromstring(page.content)
    links = webpage.xpath("//a/@href")
    for link in links:
        if link[0].isalpha() and ".mid" not in link:
            follow_link(new_base, link)
        elif ".mid" in link:
            print(link)
            response = requests.get(new_base + link)
            with open(link, mode="wb") as file:
                file.write(response.content)


main(URL)
