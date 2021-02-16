import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

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


def write_file_text(data, filepath):
    with open(filepath, "w") as file:
        file.write(data)


def write_file_cover(data, filepath):
    with open(filepath, "wb") as file:
        file.write(data)


def extract_from_link_extension(link: str) -> str:
    split_link = urlsplit(link)
    split_link_unquote = unquote(split_link.path)
    file_extension = os.path.splitext(split_link_unquote)[1]
    return file_extension


def parse_book_page(book_description_url):
    data_from_url = get_data_from_url(book_description_url)
    tululu_html = data_from_url.text
    tululu_html_soup = BeautifulSoup(tululu_html, "lxml")
    title_tag = tululu_html_soup.find("body").find(
        "div", id="content").find("h1")
    cover_link = (
        tululu_html_soup.find("body").find(
            "div", class_="bookimage").find("img")["src"]
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


def make_folder(folder):
    Path(f"./{ folder }").mkdir(parents=True, exist_ok=True)
    return folder


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
    make_folder(folder)
    book_data = get_data_from_url(url)
    full_filepath = f"{ os.path.join(folder, sanitized_filename) }.txt"
    write_file_text(book_data.text, full_filepath)
    return full_filepath


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
    make_folder(folder)
    cover_data = get_data_from_url(url)
    full_filepath = os.path.join(folder, sanitized_filename)
    write_file_cover(cover_data.content, full_filepath)
    return full_filepath


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
            print(f"Книга с индексом: { id }  не существует!\n\n")
            continue
        book_title = book_description.get("heading")
        book_cover_url = book_description.get("cover")
        book_genres = book_description.get("genres")
        book_comments = book_description.get("comments")
        book_author = book_description.get("author")
        book_text_filename = f"{ id }.{ book_title }"
        try:
            book_text_path = download_book_text(
                book_text_url, book_text_filename)
        except requests.exceptions.HTTPError:
            book_text_path = "Книга в формате txt отсутствует!"
        except requests.exceptions.ConnectionError:
            print("Что-то пошло не так:( Проверьте подключение к интернету!")
            time.sleep(4)
            continue
        try:
            book_cover_extension = extract_from_link_extension(book_cover_url)
            book_cover_filename = (
                f"{ id }_{ book_title }{ book_cover_extension }")
            book_cover_path = download_cover(
                book_cover_url, book_cover_filename)
        except (requests.exceptions.HTTPError, AttributeError):
            book_cover_path = "Обложка отсутствует!"
        except requests.exceptions.ConnectionError:
            print("Что-то пошло не так:( Проверьте подключение к интернету!")
            time.sleep(4)
            continue
        print(f'''
Индекс: { id }
Название: { book_title }
Жанр:  { book_genres }
Автор: { book_author }
Обложка: {book_cover_path}
Файл: { book_text_path }
Комментарии: { book_comments }

'''
              )


if __name__ == "__main__":
    main()
