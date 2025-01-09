import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from PIL import Image, ImageDraw
import re

BASE_URL = "https://wloczykijki.pl"
IMAGE_FOLDER = "images"  # Główny folder na zdjęcia


def get_page_content(url):
    """Pobiera zawartość strony"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Błąd {response.status_code} przy pobieraniu {url}")


def parse_main_categories(url):
    """Parsuje główne kategorie produktów"""
    content = get_page_content(url)
    soup = BeautifulSoup(content, "html.parser")
    categories = []

    # Znajdź linki do podkategorii
    for category in soup.select("div.categorydesc a"):
        categories.append({
            "url": category["href"],
            "name": category.text.strip()
        })

    return categories


def parse_products_in_category(category_url):
    """Parsuje produkty w podkategorii"""
    products = []
    content = get_page_content(category_url)
    soup = BeautifulSoup(content, "html.parser")

    # Znajdź linki do produktów
    for product in soup.select("a.prodname"):
        products.append(BASE_URL + product["href"])

    return products


def create_placeholder_image(image_path):
    """Tworzy czarny obraz zastępczy, jeśli brak zdjęcia"""
    image = Image.new("RGB", (500, 500), color="black")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Brak zdjęcia", fill="white")
    image.save(image_path, "WEBP")
    print(f"Utworzono obraz zastępczy: {image_path}")

def sanitize_filename(name):
    """Czyści nazwę pliku/folderu z niedozwolonych znaków"""
    return re.sub(r'[<>:"/\\|?*#&]', '_', name)

def download_image(image_url, category_name, product_name):
    """Pobiera i zapisuje zdjęcie do folderu kategorii"""
    category_name = sanitize_filename(category_name)
    product_name = sanitize_filename(product_name)

    # Utwórz folder dla kategorii
    category_folder = os.path.join(IMAGE_FOLDER, category_name)
    os.makedirs(category_folder, exist_ok=True)

    # Utwórz nazwę pliku
    image_name = product_name.replace(" ", "_") + os.path.splitext(image_url.split("/")[-1])[1]
    image_path = os.path.join(category_folder, image_name)

    if os.path.exists(image_path):
        print(f"Zdjęcie już istnieje: {image_path}")
        return

    # Pobierz i zapisz obraz
    try:
        # Pobierz i zapisz obraz
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Zapisano zdjęcie: {image_path}")
        else:
            print(f"Nie udało się pobrać zdjęcia: {image_url}")
            create_placeholder_image(image_path)
    except Exception as e:
        print(f"Błąd przy pobieraniu zdjęcia: {e}")
        create_placeholder_image(image_path)


def parse_product_details(product_url, category_name):
    """Pobiera szczegóły produktu i zapisuje obraz"""
    content = get_page_content(product_url)
    soup = BeautifulSoup(content, "html.parser")

    # Pobieranie szczegółów produktu
    name = soup.select_one("h1.name").text.strip()

    # Pobieranie ceny
    price_tag = soup.select_one("em.main-price.color")
    price = price_tag.text.strip() if price_tag else "Brak ceny"

    # Pobieranie obrazka
    image_tag = soup.select_one("img.photo.js__open-gallery")
    if image_tag:
        image_url = BASE_URL + image_tag["src"]
        download_image(image_url, category_name, name)
    else:
        print(f"Brak zdjęcia dla produktu: {name}")
        category_name = sanitize_filename(category_name)
        name = sanitize_filename(name)
        category_folder = os.path.join(IMAGE_FOLDER, category_name)
        os.makedirs(category_folder, exist_ok=True)
        placeholder_path = os.path.join(category_folder, f"{name}.webp")
        create_placeholder_image(placeholder_path)

    return {
        "Name": name,
        "Price": price,
        "Image": image_url if image_tag else "Brak obrazu",
        "URL": product_url
    }


def scrape_all_data(base_url):
    """Główna funkcja scrapowania wszystkich danych"""
    all_data = []

    # Krok 1: Pobierz wszystkie kategorie
    categories = parse_main_categories(base_url + "/pl/c/Alfabetycznie/275")

    # Krok 2: Dla każdej kategorii, pobierz produkty
    for category in categories:
        category_name = category["name"]
        category_url = category["url"]
        print(f"Pobieranie produktów z kategorii: {category_name}")

        products = parse_products_in_category(category_url)

        # Krok 3: Dla każdego produktu, pobierz szczegóły
        for product_url in products:
            print(f"Pobieranie danych produktu: {product_url}")
            product_details = parse_product_details(product_url, category_name)
            all_data.append(product_details)

    return all_data


def save_to_csv(data, filename="products.csv"):
    """Zapisuje dane do pliku CSV"""
    rows = []
    for item in data:
        rows.append({
            "Name": item["Name"],
            "Price": item["Price"],
            "Image": item["Image"],
            "URL": item["URL"]
        })

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Dane zapisane do pliku: {filename}")

# Start scrapera
if __name__ == "__main__":
    print("Rozpoczynam scrapowanie...")
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)  # Tworzy główny folder na zdjęcia

    data = scrape_all_data(BASE_URL)
    save_to_csv(data)

    print("Scrapowanie zakończone.")
