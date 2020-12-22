import os
from pathlib import Path

import requests


def get_text(id):
    params = {
        "id": id,
    }
    url = f"https://tululu.org/txt.php"
    response = requests.get(url, verify=False, params=params, allow_redirects=False)
    response.raise_for_status()
    if response.status_code == 302:
        return None
    return response.content


def write_file(text, directory_path, id):
    if text:
        filename = f"{ directory_path }/id{ id }.txt"
        with open(filename, "wb") as file:
            file.write(text)
        return os.path.exists(filename)
    return None


def create_directory(name):
    directory_path = f"./{ name }"
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    if os.path.exists(directory_path):
        return directory_path
    return None


if __name__ == "__main__":
    directory_path = create_directory("books")
    for id in range(1, 11):
        try:
            text = get_text(id)
            write_file(text, directory_path, id)
        except requests.exceptions.ConnectionError:
            print("Сервер не доступен!")
        except requests.exceptions.HTTPError:
            print("Ошибка в работе сервера!")