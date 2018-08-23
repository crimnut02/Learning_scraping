import re
import math
import time
import random
import codecs
import json

import requests
from bs4 import BeautifulSoup


def generate_soup_obj(url, params=None):
    return BeautifulSoup(requests.get(url, params=params).content, "lxml")


def find_total_review_count(movie_url):
    """
    Find a total review count in a target movie.
    :param movie_url: URL of the target movie.
        OK: https://movies.yahoo.co.jp/movie/362714/review/
        NO: https://movies.yahoo.co.jp/movie/未来のミライ/362741/review/
    :return:
    """
    def search_total_review_count_element(target_tag):
        ret = target_tag.name == "small" and\
              target_tag.parent['class'] == ["label"] and \
              not target_tag.string == "〜"
        return ret

    soup = generate_soup_obj(movie_url)
    count_string = soup.find(search_total_review_count_element).string
    return int(re.search(r"([0-9]+)", count_string).group())


def make_review_url_list(movie_url):
    """
    Make review urls list.
    :param movie_url: Target movie url.
    :return: review url list
    """
    base_url = "https://movies.yahoo.co.jp"
    result = list()
    total_count = find_total_review_count(movie_url)
    pages = math.ceil(total_count / 10)

    for page in range(1, pages+1):
        payload = {"page": page}
        soup = generate_soup_obj(movie_url, params=payload)
        elements = soup.find_all("a", class_="listview__element--right-icon")
        for elm in elements:
            url = base_url + elm.get("href")
            url = url[:url.index("?")] # Remove query parameter
            result.append(url)
        time.sleep(random.randint(1, 3))

    return result


def fetch_review_text(review_url, is_string=True):
    """
    Fetch review text.
    :param review_url: Target review url.
    :param is_string: Return value is one line string or not.
    :return: review txt
    """
    soup = generate_soup_obj(review_url)
    element = soup.find("p", class_="text-small text-break text-readable p1em")
    if is_string:
        return element.text.strip()
    else:
        review_string = "".join(list(map(str, element.contents)))
        return review_string.strip().replace("<br/>", "\n")


def fetch_movie_title_and_rating(movie_url):
    soup = generate_soup_obj(movie_url)
    title = soup.find("h1", class_="text-xlarge").text.replace(" ", "").replace("\n", "")
    rating_value = float(soup.find("span", {"itemprop": "ratingValue"}).string)
    return title, rating_value


def write_json_format(dist, url_list):
    output = dict()
    tmp = dict()
    for i, url in enumerate(url_list):
        tmp[i] = fetch_review_text(review_url=url, is_string=False)
        time.sleep(random.randint(1, 3))
        print(f"Complete: {url}")

    output['title'], output['rating_value'] = fetch_movie_title_and_rating(movie_url=MOVIE_URL)
    output['reviews'] = tmp

    with codecs.open(dist, "w", "utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    MOVIE_URL = "https://movies.yahoo.co.jp/movie/363528/review/"  # ペンギン・ハイウェイのレビュー
    DIST = "./penguin_highway_reviews.json"

    url_list = make_review_url_list(movie_url=MOVIE_URL)
    print("Complete making a review url list")

    write_json_format(dist=DIST, url_list=url_list)
    print("All Complete")