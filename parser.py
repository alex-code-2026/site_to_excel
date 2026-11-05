"""
Скрапер каталога интернет-магазина.
Собирает данные о товарах (название, цену, описание, картинку, категорию, наличие)
с сайта apilearn.tukas.dev. Отдает данные в виде генератора кортежей.
"""

import requests
from bs4 import BeautifulSoup
from time import sleep


Base_url = "https://apilearn.tukas.dev"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}  # чтобы сайт не подумал, что я бот


def get_url():
    """Генератор ссылок на карточки товаров со всех страниц каталога."""
    for page in range(1, 19):  # Всего 18 страниц
        sleep(2)  # уменьшить нагрузку на сайт

        url = f"{Base_url}/catalog/all/?page={page}"
        response = requests.get(url, headers=headers, timeout=10)

        # Проверка HTTP-статуса: если 4xx (404 и т.д.) или 5xx (500 и т.д.) — выбросит HTTPError
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        data = soup.find_all("div", class_="col-lg-4 col-md-6 p-4")

        for card in data:
            # Ссылка с информацией о товаре
            card_url_info = Base_url + card.find("a").get("href")
            yield card_url_info


def one_card():
    """Генератор кортежей: (название, цена, описание, картинка, категория, наличие)."""
    for card_url in get_url():
        sleep(1)
        try:
            response = requests.get(card_url, headers=headers, timeout=10)

            # Если карточка недоступна (404) или сервер упал (500) — выбросит HTTPError
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            data = soup.find("div", class_="card mb-4 custom-shadow")

            name_product = data.find("h5", class_="card-title").text.strip()

            p_tags = data.find_all("p", class_="card-text")
            information_product = p_tags[1].text.strip()

            cate = data.get("data-category")

            img_url = Base_url + data.find("img", class_="img-thumbnail").get("src")
            inventory = data.find("img", class_="img-thumbnail").get(
                "data-inventory", "?"
            )

            # Новые строки для цены
            sleep(1)
            price_slug = data.find("p", id="price-container").get("data-slug")

            api_result = requests.get(
                f"{Base_url}/api/products/{price_slug}/?format=json",
                headers=headers,
                timeout=10,
            )

            # Если API вернуло ошибку (например, 500) — выбросит HTTPError, и мы пропустим карточку
            api_result.raise_for_status()
            price_val = api_result.json().get("price", "Нет ключа price")

            yield name_product, price_val, information_product, img_url, cate, inventory

        except requests.exceptions.RequestException:
            print("Сетевая ошибка - пропускаем")
            sleep(5)
        except AttributeError:
            # Пропускаем карточку и идем на следующую страницу
            pass

    print("\n")
