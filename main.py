import os
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_data_from_url(url):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    response = requests.get(url, verify=False, allow_redirects=False)
    if response.status_code == 302 or response.raise_for_status():
        return None
    return response


def create_directory(name):
    directory_path = f"./{ name }"
    if not os.path.exists(directory_path):
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    return directory_path if os.path.exists(directory_path) else None


def write_text_to_file(data, full_path):
    with open(full_path, "w") as file:
        file.write(data)
    return full_path if os.path.exists(full_path) else None


def write_cover_to_file(data, full_path):
    with open(full_path, "wb") as file:
        file.write(data)
    return full_path if os.path.exists(full_path) else None


def parsing_data(text):
    soup = BeautifulSoup(text, "lxml")
    title_tag = soup.find("body").find("div", id="content").find("h1")
    cover_tag = soup.find("body").find("div", class_="bookimage").find("img")["src"]
    comments_tag = (
        soup.find("body").find("div", id="content").find_all("div", class_="texts")
    )
    comments_text = [
        comment.find("span", class_="black").text for comment in comments_tag
    ]
    genres_tag = (
        soup.find("body")
        .find("div", id="content")
        .find("span", class_="d_book")
        .find_all("a")
    )
    genres_text = [genre.text for genre in genres_tag]
    title, author = title_tag.text.split("::")
    url_cover_tag = urljoin("https://tululu.org/", cover_tag)
    return {
        "heading": title.strip(),
        "author": author.strip(),
        "img": url_cover_tag,
        "genre": genres_text,
        "comments": comments_text,
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
        full_filepath = f"{ os.path.join(folder, checked_filename) }.txt"
        file_path = write_text_to_file(book_data.text, full_filepath)
        return file_path
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
    file_path = []
    checked_filename = sanitize_filename(filename)
    checked_folder = sanitize_filename(folder)
    cover_data = get_data_from_url(url)
    if create_directory(checked_folder):
        full_filepath = f"{ os.path.join(folder, checked_filename) }"
        file_path = write_cover_to_file(cover_data.content, full_filepath)
    return file_path


def download_description(url):
    book_data = get_data_from_url(url)
    if book_data:
        book_description = parsing_data(book_data.text)
        return book_description
    return None


if __name__ == "__main__":
    for id in range(1, 11):
        url_book_text = f"https://tululu.org/txt.php?id={id}"
        url_book_description = f"https://tululu.org/b{id}/"
        book_description = download_description(url_book_description)
        if book_description:
            txt_name = book_description.get("heading")
            cover_url = book_description.get("img")
            genre = book_description.get("genre")
            comments = book_description.get("comments")
            cover_filename = f"{ id }.{ cover_url.split('.')[-1] }"
            txt_filename = f"{ id }.{ txt_name }"
            book_path = download_txt(url_book_text, txt_filename)
            cover_path = download_cover(cover_url, cover_filename)
            print(id, "Заголовок:", txt_name, genre)
