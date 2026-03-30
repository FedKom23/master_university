import requests
from bs4 import BeautifulSoup


def parse_product(url: str) -> dict:
    """
    Парсит страницу товара по переданному URL.

    Args:
        url (str): ссылка на страницу товара.

    Returns:
        dict: словарь с информацией о товаре:
            {
                "title": str,        # название товара
                "vendor": str,       # производитель / бренд
                "description": str,  # описание товара
                "price": float       # цена товара (число без валюты)
            }
    """
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1", id="productTitle").get_text(strip=True)
    vendor = soup.find("div", class_="brand").get_text(strip=True)
    description = soup.find("p", id="description").get_text(strip=True)
    price_text = soup.find("div", class_="price").get_text(strip=True)
    price = float(price_text.replace("₽", "").replace("\u00a0", "").replace(" ", "").strip())

    return {
        "title": title,
        "vendor": vendor,
        "description": description,
        "price": price,
    }
