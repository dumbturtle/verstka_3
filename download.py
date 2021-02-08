import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def create_input_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--start_id",
        type=int,
        default=1,
        help="Начальный индекс. По умолчанию: 1 ",
    )
    parser.add_argument(
        "-e",
        "--end_id",
        type=int,
        default=10,
        help="Последний индекс. По умолчанию: 10",
    )
    return parser


def get_data_from_url(url):
    tululu_response = requests.get(url, verify=False, allow_redirects=False)
    tululu_response.raise_for_status()
    if tululu_response.status_code == 302:
        raise requests.exceptions.HTTPError
    return tululu_response


def write_file_text(data, full_path_file):
    with open(full_path_file, "w") as file:
        file.write(data)
    return full_path_file 


def write_file_cover(data, full_path_file):
    with open(full_path_file, "wb") as file:
        file.write(data)
    return full_path_file


def parse_book_page(book_description_url):
    data_from_url = get_data_from_url(book_description_url)
    tululu_html = data_from_url.text
    tululu_html_soup = BeautifulSoup(tululu_html, "lxml")
    title_tag = tululu_html_soup.find("body").find("div", id="content").find("h1")
    cover_link = (
        tululu_html_soup.find("body").find("div", class_="bookimage").find("img")["src"]
    )
    comment_tags = (
        tululu_html_soup.find("body")
        .find("div", id="content")
        .find_all("div", class_="texts")
    )
    book_comments = [
        comment.find("span", class_="black").text for comment in comment_tags
    ]
    genre_tags = (
        tululu_html_soup.find("body")
        .find("div", id="content")
        .find("span", class_="d_book")
        .find_all("a")
    )
    book_genres = [genre.text for genre in genre_tags]
    book_title, book_author = title_tag.text.split("::")
    book_cover_full_link = urljoin(book_description_url, cover_link)
    return {
        "heading": book_title.strip(),
        "author": book_author.strip(),
        "cover": book_cover_full_link,
        "genres": book_genres,
        "comments": book_comments,
    }


def download_book_text(url, filename, folder="books/") -> str:
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    sanitized_filename = sanitize_filename(filename)
    Path(f"./{ folder }").mkdir(parents=True, exist_ok=True)
    try:
        book_data = get_data_from_url(url)
    except requests.exceptions.HTTPError:
        return "Книга в формате txt отсутствует!"
    string_filepath = f"{ os.path.join(folder, sanitized_filename) }.txt"
    file_with_data_filepath = write_file_text(book_data.text, string_filepath)
    return file_with_data_filepath


def download_cover(url, filename, folder="images/") -> str:
    """Функция для скачивания файлов изображений.
    Args:
        url (str): Cсылка изображение, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    sanitized_filename = sanitize_filename(filename)
    Path(f"./{ folder }").mkdir(parents=True, exist_ok=True)
    try:
        cover_data = get_data_from_url(url)
    except requests.exceptions.HTTPError:
        return "Обложка отсутствует!"
    string_filepath = f"{ os.path.join(folder, sanitized_filename) }"
    file_with_data_filepath = write_file_cover(cover_data.content, string_filepath)
    return file_with_data_filepath


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    input_parser = create_input_parser()
    args = input_parser.parse_args()
    for id in range(args.start_id, args.end_id + 1):
        book_text_url = f"https://tululu.org/txt.php?id={id}"
        book_description_url = f"https://tululu.org/b{id}/"
        try:
            book_description = parse_book_page(book_description_url)
        except requests.exceptions.ConnectionError:
            print("Что-то пошло не так:( Проверьте подключение к интернету!")
            time.sleep(4)
            continue
        except requests.exceptions.HTTPError:
            print(f"Книга с индексом:   { id }  не существует!\n\n")
            continue
        book_title = book_description.get("heading")
        book_cover_url = book_description.get("cover")
        book_genres = book_description.get("genres")
        book_comments = book_description.get("comments")
        book_author = book_description.get("author")
        book_cover_filename = (
            f"{ id }.{ book_title }.{ book_cover_url.split('.')[-1] }"
        )
        book_text_filename = f"{ id }.{ book_title }"
    
        book_text_path = download_book_text(book_text_url, book_text_filename)
        book_cover_path = download_cover(book_cover_url, book_cover_filename)
        print(
                f"Индекс: { id }\nНазвание: { book_title }\nАвтор: { book_author }\nОбложка: {book_cover_path} \nФайл: { book_text_path }\n\n"
            )


if __name__ == "__main__":
    main()
