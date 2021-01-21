import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def create_input_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start_id", type=int, nargs="?", default=1, help="Стартовый индекс"
    )
    parser.add_argument(
        "end_id", type=int, nargs="?", default=10, help="Последний индекс"
    )
    return parser


def get_data_from_url(url):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url, verify=False, allow_redirects=False)
    if response.status_code == 302 or response.raise_for_status():
        return None
    return response


def create_directory(name: str) -> str:
    directory_path = f"./{ name }"
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    return directory_path


def write_text_to_file(data, full_path_file):
    with open(full_path_file, "w") as file:
        file.write(data)
    return full_path_file if os.path.exists(full_path_file) else None


def write_cover_to_file(data, full_path_file):
    with open(full_path_file, "wb") as file:
        file.write(data)
    return full_path_file if os.path.exists(full_path_file) else None


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    tag_title = soup.find("body").find("div", id="content").find("h1")
    tag_cover = soup.find("body").find("div", class_="bookimage").find("img")["src"]
    tag_comments = (
        soup.find("body").find("div", id="content").find_all("div", class_="texts")
    )
    book_comments = [
        comment.find("span", class_="black").text for comment in tag_comments
    ]
    tag_genres = (
        soup.find("body")
        .find("div", id="content")
        .find("span", class_="d_book")
        .find_all("a")
    )
    book_genres = [genre.text for genre in tag_genres]
    book_title, book_author = tag_title.text.split("::")
    book_url_tag_cover = urljoin("https://tululu.org/", tag_cover)
    return {
        "heading": book_title.strip(),
        "author": book_author.strip(),
        "img": book_url_tag_cover,
        "genre": book_genres,
        "comments": book_comments,
    }


def download_txt(url, filename, folder="books/"):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    book_data = get_data_from_url(url)
    if create_directory(checked_folder) and book_data:
        string_filepath = f"{ os.path.join(folder, checked_filename) }.txt"
        filepath_file_with_data = write_text_to_file(book_data.text, string_filepath)
        return filepath_file_with_data
    return None


def download_cover(url, filename, folder="images/"):
    """Функция для скачивания файлов изображений .
    Args:
        url (str): Cсылка изображение, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filepath_file_with_data = []
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    cover_data = get_data_from_url(url)
    if create_directory(checked_folder):
        string_filepath = f"{ os.path.join(folder, checked_filename) }"
        filepath_file_with_data = write_cover_to_file(
            cover_data.content, string_filepath
        )
    return filepath_file_with_data


def download_description(url):
    book_data = get_data_from_url(url)
    if book_data:
        book_description = parse_book_page(book_data.text)
        return book_description
    return None


def main():
    input_parser = create_input_parser()
    book_range_id = input_parser.parse_args()
    for id in range(book_range_id.start_id, book_range_id.end_id + 1):
        book_text_url = f"https://tululu.org/txt.php?id={id}"
        book_description_url = f"https://tululu.org/b{id}/"
        try:
            book_description = download_description(book_description_url)
        except:
            print("Что-то пошло не так:( Проверьте подключение к интернету!")
            break
        if book_description:
            book_title = book_description.get("heading")
            book_cover_url = book_description.get("img")
            book_genres = book_description.get("genre")
            book_comments = book_description.get("comments")
            book_author = book_description.get("author")
            book_cover_filename = (
                f"{ id }.{ book_title }.{ book_cover_url.split('.')[-1] }"
            )
            book_txt_filename = f"{ id }.{ book_title }"
            book_txt_path = download_txt(book_text_url, book_txt_filename)
            if not book_txt_path:
                book_txt_path = "Книга в формате txt отсутвует!"
            book_cover_path = download_cover(book_cover_url, book_cover_filename)
            print(
                f"Индекс: { id }\nНазвание: { book_title }\nАвтор: { book_author }\nОбложка: {book_cover_path} \nФайл: { book_txt_path }\n\n"
            )


if __name__ == "__main__":
    main()