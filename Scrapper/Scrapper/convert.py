import csv
import random

# Ścieżka do pliku wejściowego i wyjściowego
input_file = "products.csv"
output_file = "output.csv"

# Funkcja do generowania unikalnych 5-cyfrowych ID
def generate_unique_id(existing_ids):
    while True:
        new_id = random.randint(10000, 99999)
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id

# Konwersja pliku
existing_ids = set()
max_elements = 100  # Maksymalna liczba elementów
processed_count = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile, delimiter=';')

    # Dodaj nagłówki z "ID" i "Quantity"
    headers = next(reader)
    headers.insert(0, "ID")  # Dodaj ID jako pierwszą kolumnę
    headers.append("Quantity")  # Dodaj Quantity na końcu
    writer.writerow(headers)

    # Przetwarzanie danych
    for row in reader:
        if processed_count >= max_elements:
            break

        # Generowanie unikalnego ID
        unique_id = generate_unique_id(existing_ids)
        row.insert(0, str(unique_id))  # Dodaj ID jako pierwszą kolumnę

        # Usuń cudzysłowy z cen i zamień na separator kropkowy
        row[2] = row[2].replace(' zł', '').replace(',', '.')

        # Dodaj ilość produktów (domyślnie np. 50)
        row.append("50")

        # Zapisz do pliku wyjściowego
        writer.writerow(row)

        processed_count += 1

print(f"Konwersja zakończona. Przetworzono maksymalnie {processed_count} elementów. Plik zapisany jako {output_file}.")
