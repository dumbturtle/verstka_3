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
    parser_id = argparse.ArgumentParser()
    parser_id.add_argument(
        "-s",
        "--start_id",
        type=int,
        default=1,
        help="Начальный индекс. По умолчанию: 1 ",
    )
    parser_id.add_argument(
        "-e",
        "--end_id",
        type=int,
        default=10,
        help="Последний индекс. По умолчанию: 10",
    )
    return parser_id


def get_data_from_url(url):
    tululu_response = requests.get(url, verify=False, allow_redirects=False)
    tululu_response.raise_for_status()
    if tululu_response.status_code == 302:
        raise requests.exceptions.HTTPError
    return tululu_response


def create_directory(name: str) -> str:
    directory_path = f"./{ name }"
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    return directory_path


def write_text_to_file(data, full_path_file):
    with open(full_path_file, "w") as file:
        file.write(data)
    return full_path_file 


def write_cover_to_file(data, full_path_file):
    with open(full_path_file, "wb") as file:
        file.write(data)
    return full_path_file


def parse_book_page(html_content):
    tululu_html_soup = BeautifulSoup(html_content.text, "lxml")
    title_tag = tululu_html_soup.find("body").find("div", id="content").find("h1")
    cover_tag = (
        tululu_html_soup.find("body").find("div", class_="bookimage").find("img")["src"]
    )
    comments_tag = (
        tululu_html_soup.find("body")
        .find("div", id="content")
        .find_all("div", class_="texts")
    )
    book_comments = [
        comment.find("span", class_="black").text for comment in comments_tag
    ]
    genres_tag = (
        tululu_html_soup.find("body")
        .find("div", id="content")
        .find("span", class_="d_book")
        .find_all("a")
    )
    book_genres = [genre.text for genre in genres_tag]
    book_title, book_author = title_tag.text.split("::")
    book_cover_url = urljoin("https://tululu.org/", cover_tag)
    return {
        "heading": book_title.strip(),
        "author": book_author.strip(),
        "cover": book_cover_url,
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
    checked_filename = sanitize_filename(filename)
    Path(f"./{ folder }").mkdir(parents=True, exist_ok=True)
    try:
        book_data = get_data_from_url(url)
    except requests.exceptions.HTTPError:
        return "Книга в формате txt отсутствует!"
    string_filepath = f"{ os.path.join(folder, checked_filename) }.txt"
    file_with_data_filepath = write_text_to_file(book_data.text, string_filepath)
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
    checked_filename = sanitize_filename(filename)
    Path(f"./{ folder }").mkdir(parents=True, exist_ok=True)
    try:
        cover_data = get_data_from_url(url)
    except requests.exceptions.HTTPError:
        return "Обложка отсутствует!"
    string_filepath = f"{ os.path.join(folder, checked_filename) }"
    file_with_data_filepath = write_cover_to_file(cover_data.content, string_filepath)
    return file_with_data_filepath


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    input_parser = create_input_parser()
    args = input_parser.parse_args()
    for id in range(args.start_id, args.end_id + 1):
        book_text_url = f"https://tululu.org/txt.php?id={id}"
        book_description_url = f"https://tululu.org/b{id}/"
        try:
            book_data = get_data_from_url(book_description_url)
            book_description = parse_book_page(book_data)
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
