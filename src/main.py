# farmatodo_scrapper/src/main.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from scrapper import obtener_info_producto
from utils import guardar_datos
from typing import Dict, List, Any

default_columns = ["Item", "categoría", "sub categoría", "Descripción Item", "División"]

def filter_object_by_keys(obj: Dict[str, Any], keys_to_keep: List[str]) -> Dict[str, Any]:
    """
    Filters a dictionary to include only the keys present in the provided list.

    Args:
        obj: The dictionary to filter.
        keys_to_keep: A list of keys to keep in the resulting dictionary.

    Returns:
        A new dictionary containing only the keys from keys_to_keep that
        were found in the original dictionary and their corresponding values.
    """
    filtered_obj = {}
    for key in keys_to_keep:
        if key in obj:
            filtered_obj[key] = obj[key]
    return filtered_obj

def main():
    """
    Lee el archivo Excel de entrada, realiza el scraping para cada ID
    y guarda los resultados en un nuevo archivo Excel.
    """
    try:
        df_input = pd.read_excel("data/input.xlsx")
        if 'Item' not in df_input.columns:
            print("La columna 'Item' no se encontró en el archivo input.xlsx.")
            return

        resultados = []
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

        for index, row in df_input.iterrows():


            defaults = filter_object_by_keys(row, default_columns)
            item_id = str(row['Item'])  # Asegurarse de que el ID sea una cadena
            print(f"Scrapeando información para el ítem: {item_id}")
            info_producto = obtener_info_producto(item_id,driver, defaults)
            if info_producto:
                resultados.append(info_producto)
        if driver:
            driver.quit()

        if resultados:
            guardar_datos(resultados, "output/output.xlsx")
        else:
            print("No se encontraron datos para guardar.")

    except FileNotFoundError:
        print("El archivo input.xlsx no se encontró en la carpeta 'data'.")
    except Exception as e:
        print(f"Ocurrió un error general: {e}")

if __name__ == "__main__":
    main()