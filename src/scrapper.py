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


def get_attribute_text(driver, metadata, attribute_name):
    """
    Intenta encontrar un elemento usando el selector CSS y devuelve su texto.
    Maneja la excepción si el elemento no se encuentra.
    """
    try:
        # Usamos find_element para obtener el primer elemento que coincida
        # con cualquiera de las partes del selector CSS combinado con comas.
        # element = driver.find_element(By.CSS_SELECTOR, selector)
        # Aquí podrías necesitar lógica adicional para extraer el valor específico
        # si el selector apunta a un contenedor más grande.
        # Por ahora, devolvemos el texto completo del primer elemento encontrado.
        element = driver.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "#app-component-router-outlet > div > div.routers-views > div > app-product-detail"
            )))
        if metadata[attribute_name]['found_value'] is not None:
            # Si el valor encontrado es uno de los valores esperados, lo devolvemos
            if encontrar_palabras_relacionadas(
                    element.text.strip(),
                    metadata[attribute_name]['selector']):
                return metadata[attribute_name]['found_value']
            else:
                return metadata[attribute_name]['default_value']
        if metadata[attribute_name]['found_value'] is None:
            # Si no hay valor por defecto, devolvemos el texto del elemento
            return encontrar_palabra_mas_relacionada(
                element.text.strip(),
                metadata[attribute_name]['related_keywords'])
        return metadata[attribute_name]['default_value']
    except NoSuchElementException:
        # print(f"Atributo '{attribute_name}' no encontrado con el selector: {selector}")
        return metadata[attribute_name][
            "default_value"]  # O devuelve un valor predeterminado como 'No especificado'


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
        button_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".box__see")))
        button_element.click()
        wait.until(lambda driver: driver.execute_script('return document.readyState === "complete"'), message="Page load incomplete after button click.")
        
        driver.implicitly_wait(0.3)  # 300 milliseconds

        data_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".container-data-sheet .item")))
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
    finally:
        driver.implicitly_wait(0)

# Recuerda cerrar el driver al final
# driver.quit()
def obtener_info_producto(driver):
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
            item[key] = get_attribute_text(wait, product_selectors, key)

        # Esperar a que el elemento del precio esté presente (ejemplo)
        precio_elemento = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '#app-component-router-outlet > div > div.routers-views > div > app-product-detail > div.container-fluid.cont-product-detail > div.row.m-0.mktpl-product-detail.py-2.py-lg-4 > div.col-12.d-none.d-md-inline-block.col-lg-3.pr-0.pt-4 > div > app-mktpl-price-box > div > div.box__price > span'
            )))
        precio = precio_elemento.text.strip()

        return {'Item': item_id, 'Nombre': nombre, **item, **basic_information}
    except Exception as e:
        print(f"Error al procesar la página del producto {item_id}: {e}")
        return None


if __name__ == '__main__':
    # Ejemplo de cómo usar la función (se ejecuta solo si este archivo es el principal)
    info = obtener_info_producto("1001038")
    if info:
        print(info)
