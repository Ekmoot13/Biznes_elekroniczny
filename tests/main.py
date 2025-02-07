from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import time
import urllib3

# Wyłączenie ostrzeżeń SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL sklepu i kategorii
SHOP_URL = "https://localhost/index.php"
CATEGORY_URL_1 = "https://localhost/index.php?id_category=579&controller=category&id_lang=1"
CATEGORY_URL_2 = "https://localhost/index.php?id_category=580&controller=category&id_lang=1"

# Konfiguracja przeglądarki
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-insecure-localhost')

# Inicjalizacja WebDrivera
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def add_products_from_category(driver, category_url, products_count):
    """Dodaje określoną liczbę produktów z podanej kategorii do koszyka."""
    driver.get(category_url)
    print(f"Przejście do kategorii: {category_url}")

    for _ in range(products_count):
        # Poczekaj na załadowanie produktów
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.js-product.product.col-xs-12.col-sm-6.col-xl-4'))
        )

        # Znajdź wszystkie produkty na stronie
        products = driver.find_elements(By.CSS_SELECTOR, '.js-product.product.col-xs-12.col-sm-6.col-xl-4')

        # Wybierz losowy produkt
        chosen_product = random.choice(products)
        product_link = chosen_product.find_element(By.TAG_NAME, 'a')
        driver.execute_script("arguments[0].scrollIntoView(true);", product_link)
        product_link.click()

        try:
            # Kliknij przycisk "Dodaj do koszyka"
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.add-to-cart'))
            ).click()
            print("Produkt dodany do koszyka.")

            # Poczekaj na pojawienie się modalu
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'cart-content-btn'))
            )
            print("Modal potwierdzenia dodania produktu się pojawił.")

            # Kliknij "Kontynuuj zakupy" w modalu
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-secondary'))
            ).click()
            print("Kontynuacja zakupów.")
        except Exception as e:
            print(f"Błąd podczas dodawania produktu do koszyka: {e}")

        # Powróć do strony kategorii
        driver.back()
        print("Powrót do strony kategorii.")


def search_and_add_product(driver, search_term):
    """Wyszukuje produkt i dodaje losowy wynik do koszyka."""
    driver.get(SHOP_URL)
    search_box = driver.find_element(By.CSS_SELECTOR, '.ui-autocomplete-input')
    search_box.send_keys('Włóczka Symfonie Viva VR1008')
    search_box.send_keys('\n')
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.js-product.product.col-xs-12.col-sm-6.col-xl-3'))
    )
    products = driver.find_elements(By.CSS_SELECTOR, '.js-product.product.col-xs-12.col-sm-6.col-xl-3')
    chosen_product = random.choice(products)
    chosen_product.find_element(By.TAG_NAME, 'a').click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.add-to-cart'))
    ).click()
    print(f"Produkt z wyszukiwania dodano do koszyka.")

def remove_products_from_cart(driver, count):
    """Usuń określoną liczbę produktów z koszyka."""
    try:
        # Otwórz koszyk
        cart_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#_desktop_cart a'))
        )
        cart_link.click()

        # Usuń produkty
        for _ in range(count):
            products = driver.find_elements(By.CLASS_NAME, 'cart-items')
            if not products:
                print("Brak produktów w koszyku do usunięcia.")
                return
            products[0].find_element(By.CLASS_NAME, 'remove-from-cart').click()
            print("Usunięto produkt z koszyka.")
    except Exception as e:
        print(f"Błąd podczas usuwania produktów z koszyka: {e}")

def proceed_to_checkout(driver):
    """Przejście do realizacji zamówienia z koszyka."""
    try:
        # Poczekaj na widoczność przycisku "Przejdź do realizacji zamówienia"
        checkout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary'))
        )
        checkout_button.click()
        print("Przeszliśmy do realizacji zamówienia.")
    except Exception as e:
        print(f"Błąd podczas przechodzenia do realizacji zamówienia: {e}")


def register_account(driver):
    """Rejestracja nowego użytkownika."""
    try:
        # Wypełnij pola formularza rejestracji
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'customer-form'))
        )
        driver.find_element(By.ID, 'field-id_gender-1').click()  # Pan
        driver.find_element(By.ID, 'field-firstname').send_keys("Jan")
        driver.find_element(By.ID, 'field-lastname').send_keys("Kowalski")
        driver.find_element(By.ID, 'field-email').send_keys("jan.kowalski7@example.com")
        driver.find_element(By.ID, 'field-password').send_keys("BezpieczneHaslo123")
        driver.find_element(By.ID, 'field-birthday').send_keys("1990-01-01")

        # Opcjonalne: zaznaczenie zgód
        driver.find_element(By.NAME, 'optin').click()  # Oferty partnerów
        driver.find_element(By.NAME, 'newsletter').click()  # Newsletter

        driver.find_element(By.NAME, 'continue').click()
        print("Zapisano nowego użytkownika.")
    except Exception as e:
        print(f"Błąd podczas rejestracji użytkownika: {e}")
    finally:
        time.sleep(1)  # Opcjonalne: czas na obserwację wyniku


def complete_order(driver):
    """Kompletuje zamówienie."""
    # Poczekaj, aż pole adresowe będzie widoczne
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'field-address1'))
    )
    driver.find_element(By.ID, 'field-address1').send_keys("123 Testowa")
    driver.find_element(By.ID, 'field-postcode').send_keys("00-123")
    driver.find_element(By.ID, 'field-city').send_keys("Warszawa")

    # Poczekaj, aż przycisk "Potwierdź adresy" będzie klikalny
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'confirm-addresses'))
    ).click()
    print("Wypełniono dane adresowe.")

    # Poczekaj, aż opcja dostawy będzie widoczna i kliknij
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'delivery_option_1'))
    )
    driver.find_element(By.ID, 'delivery_option_8').click()

    # Poczekaj, aż przycisk "Potwierdź dostawę" będzie klikalny
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'confirmDeliveryOption'))
    ).click()

    # Poczekaj, aż opcja płatności będzie widoczna i kliknij
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'payment-option-1'))
    )
    driver.find_element(By.ID, 'payment-option-1').click()

    # Poczekaj, aż checkbox zgody na regulamin będzie widoczny i kliknij
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'condition-label'))
    )
    driver.find_element(By.CLASS_NAME, 'condition-label').click()

    # Poczekaj, aż przycisk "Zatwierdź zamówienie" będzie klikalny
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.center-block'))
    ).click()
    print("Zamówienie zostało zatwierdzone.")


def test_purchase_workflow():
    """Pełny test zgodny z wymaganiami."""
    try:
        add_products_from_category(driver, CATEGORY_URL_1, 10)
        #add_products_from_category(driver, CATEGORY_URL_2, 5)
        search_and_add_product(driver, "Testowy produkt")
        remove_products_from_cart(driver, 3)
        proceed_to_checkout(driver)
        register_account(driver)
        complete_order(driver)
        print("Test zakończony pomyślnie.")
    except Exception as e:
        print(f"Błąd podczas testu: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_purchase_workflow()
