import os
from pathlib import Path

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


def write_data_to_file(data, full_path):
    with open(full_path, "w") as file:
        file.write(data)
    return full_path if os.path.exists(full_path) else None


def parsing_data(text):
    soup = BeautifulSoup(text, "lxml")
    title_tag = soup.find("body").find("div", id="content").find("h1")
    title, author = title_tag.text.split("::")
    return {"heading": title.strip(), "author": author.strip()}


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
    book_text = get_data_from_url(url)
    if create_directory(checked_folder) and book_text:
        full_filepath = f"{ os.path.join(folder, checked_filename) }.txt"
        file_path = write_data_to_file(book_text.text, full_filepath)
        return file_path
    return None


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
            filename = book_description.get("heading")
            book_path = download_txt(url_book_text, filename)
            print(id, book_path)
