<?php
require_once(dirname(__FILE__) . '/config/config.inc.php');
require_once(dirname(__FILE__) . '/init.php');

// Pobierz wszystkie produkty
$products = Product::getProducts(Context::getContext()->language->id, 0, 0, 'id_product', 'ASC');

foreach ($products as $product) {
    $productObj = new Product($product['id_product']);
    try {
        $productObj->delete(); // Usuń produkt
        echo "Usunięto produkt o ID: " . $product['id_product'] . "\n";
    } catch (Exception $e) {
        echo "Błąd podczas usuwania produktu o ID: " . $product['id_product'] . " - " . $e->getMessage() . "\n";
    }
}

echo "Wszystkie produkty zostały usunięte.\n";
?>
