import requests


def get_text():
    url = f"https://tululu.org/txt.php?id=32168"
    response = requests.get(url, verify=False)
    response.raise_for_status()
    filename = 'book.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)
    return "Ok"


if __name__ == "__main__":
    try:
        print(get_text())
    except requests.exceptions.ConnectionError:
        print("Сервер не доступен!")
    except requests.exceptions.HTTPError:
        print("Ошибка в работе сервера!")
