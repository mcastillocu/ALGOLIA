# farmatodo_scrapper/src/utils.py
import pandas as pd

def guardar_datos(data, nombre_archivo="output/output.xlsx"):
    """Guarda los datos en un archivo Excel."""
    df = pd.DataFrame(data)
    df.to_excel(nombre_archivo, index=False)
    print(f"Datos guardados en: {nombre_archivo}")

if __name__ == '__main__':
    # Ejemplo de cómo usar la función (se ejecuta solo si este archivo es el principal)
    ejemplo_data = [{'Item': '123', 'Nombre': 'Producto de prueba', 'Precio': '10.000'},
                   {'Item': '456', 'Nombre': 'Otro producto', 'Precio': '25.000'}]
    guardar_datos(ejemplo_data)