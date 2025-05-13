# farmatodo_scrapper/src/scrapper.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
# Importa aquí tu configuración del WebDriver (e.g., webdriver.Chrome())

# --- Selectores CSS (Compatibles con Selenium) ---

# --- General / Dietary ---
vegan_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='vegan']"
gluten_free_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='gluten']"
sugar_free_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='sugar-free']"
organico_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='organic']"
natural_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='natural']"
sin_aditivos_selector = "div#características, div#descripción"
vegetariano_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='vegetarian']"
keto_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='keto']"
bajo_sodio_selector = "div#características, div#descripción"
fuente_proteina_selector = "div#características, div#descripción"
fuente_fibra_selector = "div#características, div#descripción"
fuente_vitaminas_selector = "div#características, div#descripción"
apto_diabeticos_selector = "div#características, div#descripción"
apto_celiacos_selector = "div#características, div#descripción"
con_edulcorantes_naturales_selector = "div#características, div#descripción"
con_edulcorantes_artificiales_selector = "div#características, div#descripción"
sin_lactosa_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='lactose-free']"

# --- Cosmetics / Personal Care ---
talla_selector = "div#características, div.mktpl-add-cart select[name*='size'], div.mktpl-add-cart .variation-selector.size"
tipo_piel_selector = "div#características, div#descripción"
tipo_cabello_selector = "div#características, div#descripción"
tono_color_selector = "div#características, div.mktpl-add-cart .color-swatch, div.mktpl-add-cart select[name*='color']"
acabado_selector = "div#características, div#descripción"
cobertura_selector = "div#características, div#descripción"
formato_cosmetico_selector = "div#características, div#descripción"
con_fragancia_selector = "div#características, div#descripción"
con_proteccion_solar_selector = "div#características, div#descripción"
fps_selector = "div#características, div#descripción, h1 + span.fps, .product-detail-container__title + span.fps"
con_color_selector = "div#características, div#descripción"
zonas_uso_selector = "div#características, div#descripción"
libre_alcohol_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='alcohol-free']"
libre_aceites_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='oil-free']"
libre_parabenos_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='paraben-free']"
libre_comedogenicos_selector = "div#características, div#descripción"
con_enjuague_selector = "div#características, div#descripción" # Requires Rinse

# --- Baby / Child ---
etapa_selector = "div#características, div#descripción" # e.g., Etapa bebé
edad_recomendada_etapa_bebe_selector = "div#características, div#descripción"
formato_bebe_selector = "div#características, div#descripción"
material_textura_bebe_selector = "div#características, div#descripción"
anti_derrames_colicos_bacteriano_selector = "div#características, div#descripción"
con_bpa_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='bpa-free']" # Often shown as BPA-Free
compatible_esterilizadores_selector = "div#características, div#descripción"
facilidad_digestion_selector = "div#características, div#descripción"

# --- Health / Ingredients / Safety ---
ingredientes_activos_selector = "div#descripción ul, div#características ul, div#descripción .ingredients, div#características .ingredients"
hipoalergenico_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='hypoallergenic']"
con_ingredientes_naturales_selector = "div#características, div#descripción, app-mktpl-product-detail [class*='natural']"
sin_conservantes_selector = "div#características, div#descripción"
con_alcohol_selector = "div#características, div#descripción" # Contrast to libre_alcohol_selector
certificaciones_selector = "div#características, div#descripción, .certifications img"

# --- Functionality / Usage / Durability ---
funcion_beneficio_selector = "div#descripción, div#características"
duracion_resistencia_agua_selector = "div#características, div#descripción"
proteccion_24h_resistente_agua_selector = "div#características, div#descripción" # More specific duration/resistance
forma_consumo_selector = "div#descripción, div#características"
incluye_accesorios_selector = "div#descripción, div#características"
compatibilidad_varios_selector = "div#características, div#descripción" # For dishwasher/microwave/pets/surfaces
durabilidad_resistencia_selector = "div#características, div#descripción"
uso_interior_exterior_selector = "div#características, div#descripción"
compatibilidad_apps_maquinas_selector = "div#características, div#descripción"

# --- Home ---
funcion_hogar_selector = "div#características, div#descripción"
fragancia_hogar_selector = "div#características, div#descripción"
biodegradable_selector = "div#características, div#descripción"
reutilizable_selector = "div#características, div#descripción"

# --- Pets ---
sabor_aroma_selector = "div#características, div#descripción" # For pets or food
beneficio_mascotas_selector = "div#características, div#descripción"

# --- Sports / Supplements ---
tipo_suplemento_selector = "div#características, div#descripción"
objetivo_beneficio_deportivo_selector = "div#características, div#descripción"
sabor_deportivo_selector = "div#características, div#descripción"
presentacion_suplemento_selector = "div#características, div#descripción"
con_cafeina_selector = "div#características, div#descripción"
tipo_deporte_selector = "div#características, div#descripción"


# --- Ejemplo de uso en Selenium ---

# Asume que 'driver' es tu instancia de WebDriver ya configurada y
# que has navegado a la página del producto.

def get_attribute_text(driver, selector, attribute_name):
    """
    Intenta encontrar un elemento usando el selector CSS y devuelve su texto.
    Maneja la excepción si el elemento no se encuentra.
    """
    try:
        # Usamos find_element para obtener el primer elemento que coincida
        # con cualquiera de las partes del selector CSS combinado con comas.
        element = driver.find_element(By.CSS_SELECTOR, selector)
        # Aquí podrías necesitar lógica adicional para extraer el valor específico
        # si el selector apunta a un contenedor más grande.
        # Por ahora, devolvemos el texto completo del primer elemento encontrado.
        return element.text.strip()
    except NoSuchElementException:
        # print(f"Atributo '{attribute_name}' no encontrado con el selector: {selector}")
        return None # O devuelve un valor predeterminado como 'No especificado'
# Recuerda cerrar el driver al final
# driver.quit()
def obtener_info_producto(item_id,driver):
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

        nombre_elemento = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#app-component-router-outlet > div > div.routers-views > div > app-product-detail > div.container-fluid.cont-product-detail > div.row.m-0.mktpl-product-detail.py-2.py-lg-4 > div.col-12.col-lg-9.px-0 > div.row.m-0 > div.col-12.col-lg-4.px-0.py-2.py-lg-5 > app-mktpl-product-detail > div > h1')))
        nombre = nombre_elemento.text.strip()
        diabeticos_text = get_attribute_text(driver, apto_diabeticos_selector, "Apto para Diabéticos")


        # Esperar a que el elemento del precio esté presente (ejemplo)
        precio_elemento = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#app-component-router-outlet > div > div.routers-views > div > app-product-detail > div.container-fluid.cont-product-detail > div.row.m-0.mktpl-product-detail.py-2.py-lg-4 > div.col-12.d-none.d-md-inline-block.col-lg-3.pr-0.pt-4 > div > app-mktpl-price-box > div > div.box__price > span')))
        precio = precio_elemento.text.strip()

        return {'Item': item_id, 'Nombre': nombre, 'Precio': precio}
    except Exception as e:
        print(f"Error al procesar la página del producto {item_id}: {e}")
        return None

if __name__ == '__main__':
    # Ejemplo de cómo usar la función (se ejecuta solo si este archivo es el principal)
    info = obtener_info_producto("1001038")
    if info:
        print(info)