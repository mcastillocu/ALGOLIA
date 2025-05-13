import spacy

# --- Cargar el modelo de spaCy UNA VEZ ---
# Cargar el modelo fuera de la función es más eficiente,
# ya que la carga del modelo es costosa.
# Intentamos cargar el modelo 'md'. Si no está, damos instrucciones.
try:
    nlp = spacy.load("es_core_news_md")
    print("Modelo de spaCy 'es_core_news_md' cargado correctamente.")
except IOError:
    print("Error: Modelo de spaCy 'es_core_news_md' no encontrado.")
    print("Por favor, descárgalo ejecutando en tu terminal lo siguiente:")
    print("python -m spacy download es_core_news_md")
    nlp = None  # Si no se carga, nlp será None


def encontrar_palabra_mas_relacionada(
        texto: str,
        palabras_objetivo: list[str]) -> tuple[str | None, float | None]:
    """
    Encuentra la palabra en el texto que tiene la mayor similitud semántica
    con cualquiera de las palabras en la lista de palabras objetivo.

    Args:
        texto (str): El texto donde buscar.
        palabras_objetivo (list[str]): Una lista de palabras o frases objetivo.

    Returns:
        tuple[str | None, float | None]: Una tupla conteniendo la palabra del
                                         texto con la mayor similitud y su valor
                                         de similitud. Retorna (None, None) si
                                         no se encuentra ninguna palabra con vector
                                         o si la lista de palabras objetivo está vacía.
    """
    if nlp is None:
        print("El modelo de spaCy no está disponible. No se puede procesar.")
        return None, None

    if not palabras_objetivo:
        print("Advertencia: La lista de palabras objetivo está vacía.")
        return None, None

    doc_texto = nlp(texto)
    docs_objetivo = [nlp(palabra) for palabra in palabras_objetivo]

    # Verificar si alguna de las palabras objetivo tiene vector
    tiene_vector_objetivo = any(doc.has_vector for doc in docs_objetivo)
    if not tiene_vector_objetivo:
        print(
            "Advertencia: Ninguna de las palabras objetivo tiene un vector asociado en el modelo."
        )
        return None, None

    mejor_palabra = None
    max_similitud = -1.0

    for token_texto in doc_texto:
        if token_texto.is_punct or token_texto.is_space:
            continue
        if not token_texto.has_vector:
            continue

        for doc_objetivo in docs_objetivo:
            if doc_objetivo.has_vector:
                similitud = token_texto.similarity(doc_objetivo)
                if similitud > max_similitud:
                    max_similitud = similitud
                    mejor_palabra = doc_objetivo.text

    if mejor_palabra:
        return mejor_palabra, max_similitud
    else:
        return None, None


# --- Ejemplos de Uso ---

if __name__ == "__main__":
    texto1 = "El perro corre rápido por el parque. El canino parece feliz."
    palabras1 = ["perro", "gato"]
    mejor_coincidencia1, similitud1 = encontrar_palabra_mas_relacionada(
        texto1, palabras1)
    print(f"Texto: '{texto1}'")
    print(f"Palabras objetivo: '{palabras1}'")
    if mejor_coincidencia1:
        print(
            f"La palabra más relacionada es: '{mejor_coincidencia1}' con una similitud de: {similitud1:.2f}"
        )
    else:
        print(
            "No se encontraron palabras relacionadas con las palabras objetivo."
        )
    print("-" * 20)

    texto2 = "El coche rojo es muy veloz y moderno."
    palabras2 = ["automóvil", "moto", "bicicleta"]
    mejor_coincidencia2, similitud2 = encontrar_palabra_mas_relacionada(
        texto2, palabras2)
    print(f"Texto: '{texto2}'")
    print(f"Palabras objetivo: '{palabras2}'")
    if mejor_coincidencia2:
        print(
            f"La palabra más relacionada es: '{mejor_coincidencia2}' con una similitud de: {similitud2:.2f}"
        )
    else:
        print(
            "No se encontraron palabras relacionadas con las palabras objetivo."
        )
    print("-" * 20)

    texto3 = "La casa grande tiene un jardín hermoso."
    palabras3 = ["apartamento", "vivienda"]
    mejor_coincidencia3, similitud3 = encontrar_palabra_mas_relacionada(
        texto3, palabras3)
    print(f"Texto: '{texto3}'")
    print(f"Palabras objetivo: '{palabras3}'")
    if mejor_coincidencia3:
        print(
            f"La palabra más relacionada es: '{mejor_coincidencia3}' con una similitud de: {similitud3:.2f}"
        )
    else:
        print(
            "No se encontraron palabras relacionadas con las palabras objetivo."
        )
    print("-" * 20)

    texto4 = "El libro trata sobre la inteligencia artificial."
    palabras4 = ["ciencia ficción", "aprendizaje automático"]
    mejor_coincidencia4, similitud4 = encontrar_palabra_mas_relacionada(
        texto4, palabras4)
    print(f"Texto: '{texto4}'")
    print(f"Palabras objetivo: '{palabras4}'")
    if mejor_coincidencia4:
        print(
            f"La palabra más relacionada es: '{mejor_coincidencia4}' con una similitud de: {similitud4:.2f}"
        )
    else:
        print(
            "No se encontraron palabras relacionadas con las palabras objetivo."
        )
    print("-" * 20)
