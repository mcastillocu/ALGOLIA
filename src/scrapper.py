# farmatodo_scrapper/src/scrapper.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from metadata import product_selectors
from find_words import encontrar_palabras_relacionadas
from encontrar_palabra_mas_relacionada import encontrar_palabra_mas_relacionada
from typing import Dict, List, Any, Optional
from selenium.common.exceptions import TimeoutException


# Importa aquí tu configuración del WebDriver (e.g., webdriver.Chrome())

# --- Selectores CSS (Compatibles con Selenium) ---

# Diccionario de selectores CSS para Selenium, mapeando las claves proporcionadas

# --- Notas Importantes para tu Scraper ---
# 4.  Procesamiento Post-Extracción: Para los atributos booleanos (Sí/No) o con valores
#     específicos (Alta/Media/Baja), después de extraer el texto con Selenium, necesitarás
#     lógica adicional para convertir ese texto en el valor deseado (True/False, 'Alta', etc.).
# 5.  Error Handling: Siempre usa try/except NoSuchElementException al buscar cada elemento
#     con Selenium, ya que no todos los atributos estarán presentes en todos los productos.
#Necesitamos validar si la key tiene un si/no o un valor específico para la selección del texto o hacer un análsis después con el excel

# Asume que 'driver' es tu instancia de WebDriver ya configurada y
# que has navegado a la página del producto.


def get_attribute_text_scraper(driver: WebDriver, wait: WebDriverWait, metadata: Dict[str, Any], attribute_name: str) -> Optional[str]:
    """
    Extracts and processes text content from specific elements on a webpage based on metadata.

    Args:
        driver: A Selenium WebDriver instance.
        wait: A WebDriverWait instance.
        metadata: A dictionary containing information about the attributes to extract,
                  including selectors, expected values, default values, and related keywords.
        attribute_name: The name of the attribute to extract.

    Returns:
        The extracted and processed text content, or a default value if not found or processed.
    """
    informacion = ""
    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "h1.product-detail-container__title")
        informacion += title_element.text.replace(r'\W+', ' ')
    except NoSuchElementException:
        pass

    try:
        description_element = driver.find_element(By.CSS_SELECTOR, "p.product-detail-container__description")
        informacion += " " + description_element.text.replace(r'\W+', ' ')
    except NoSuchElementException:
        pass

    try:
        seo_element = driver.find_element(By.CSS_SELECTOR, "div.seo-container")
        informacion += " " + seo_element.text.replace(r'\W+', ' ')
    except NoSuchElementException:
        pass

    if attribute_name in metadata:
        attribute_data = metadata[attribute_name]
        found_value = attribute_data.get('found_value')
        default_value = attribute_data.get('default_value')
        selector = attribute_data.get('selector')
        related_keywords = attribute_data.get('related_keywords')

        if found_value is not None:
            # Assuming encontrar_palabras_relacionadas is a function you have defined elsewhere
            if selector and encontrar_palabras_relacionadas(informacion, selector):
                return found_value
            else:
                return default_value
        elif related_keywords:
            # Assuming encontrar_palabra_mas_relacionada is a function you have defined elsewhere
            word, umbral = encontrar_palabra_mas_relacionada(informacion, related_keywords)
            if umbral >= 0.7:
                return word
            else:
                return default_value
        else:
            return default_value
    else:
        return None 


def extract_default_columns_from_web_scraper(item_id: str, driver: WebDriver, wait) -> dict:
    """
    Extracts data from specific elements on a webpage after clicking a button.

    Args:
        item_id: An identifier for the item being processed (for logging or context).
        driver: A Selenium WebDriver instance.

    Returns:
        A dictionary where keys are extracted titles (without the trailing colon)
        and values are their corresponding descriptions. Returns an empty dictionary
        if the button or data elements are not found within the timeout.
    """
    try:
        

        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".box__see"))).click()
        except Exception as e_click:
            print(f"Error clicking the button for item {item_id}: {e_click}")
            try:
                button_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".box__see")))
                driver.execute_script("arguments[0].click();", button_element)
            except Exception as e_js_click:
                print(f"Error clicking the button via JavaScript for item {item_id}: {e_js_click}")
                try:
                    button_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".box__see")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", button_element)
                    import time
                    time.sleep(0.5)
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".box__see"))).click()
                except Exception as e_scroll_click:
                    print(f"Error clicking after scrolling for item {item_id}: {e_scroll_click}")
                    return {} 

        driver.implicitly_wait(0.5)  

        data_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".container-data-sheet .item")))
        
        driver.implicitly_wait(0.5) 
        extracted_data = {}
        for item in data_elements:
            try:
                title_element = item.find_element(By.CSS_SELECTOR, ".title")
                description_element = item.find_element(By.CSS_SELECTOR, ".description")
                title = title_element.text.rstrip(':')
                description = description_element.text
                extracted_data[title] = description
            except Exception as e:
                print(f"Error extracting data for item {item_id}: {e}")
                continue 

        return extracted_data

    except TimeoutException:
        print(f"Timeout occurred while trying to find or interact with elements for item {item_id}.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while extracting data for item {item_id}: {e}")
        return {}

# Recuerda cerrar el driver al final
# driver.quit()
def obtener_info_producto(item_id, driver, defaults: Dict[str, Any]):
    """
    Abre una página del producto en un navegador, espera a que el contenido cargue
    y extrae la información.

    Args:
        item_id (str): El ID del producto.

    Returns:
        dict: Un diccionario con la información del producto (nombre, precio, etc.),
              o None si ocurre un error o el producto no se encuentra.
    """
    url = f"https://www.farmatodo.com.co/producto/{item_id}"
    try:
        driver.get(url)

        # Esperar a que el elemento del nombre del producto esté presente (ejemplo)
        wait = WebDriverWait(driver, 10)
        driver.implicitly_wait(1) 
        basic_information = extract_default_columns_from_web_scraper(item_id, driver, wait)
        nombre_elemento = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '#app-component-router-outlet > div > div.routers-views > div > app-product-detail > div.container-fluid.cont-product-detail > div.row.m-0.mktpl-product-detail.py-2.py-lg-4 > div.col-12.col-lg-9.px-0 > div.row.m-0 > div.col-12.col-lg-4.px-0.py-2.py-lg-5 > app-mktpl-product-detail > div > h1'
            )))
        nombre = nombre_elemento.text.strip()
        item = dict()
        for key, selector in product_selectors.items():
            # Usar la función get_attribute_text para obtener el texto del atributo
            item[key] = get_attribute_text_scraper(driver, wait, product_selectors, key)

        return {'Item': item_id, 'Nombre': nombre, **defaults, **item, **basic_information}
    except Exception as e:
        print(f"Error al procesar la página del producto {item_id}: {e}")
        return None


if __name__ == '__main__':
    # Ejemplo de cómo usar la función (se ejecuta solo si este archivo es el principal)
    info = obtener_info_producto("1001038")
    if info:
        print(info)
