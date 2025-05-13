import spacy

# --- Cargar el modelo de spaCy UNA VEZ ---
# Cargar el modelo fuera de la función es más eficiente.
# Intentamos cargar el modelo 'md'. Si no está, damos instrucciones.
try:
    nlp = spacy.load("es_core_news_md")
    print("Modelo de spaCy 'es_core_news_md' cargado correctamente.")
except IOError:
    print("Error: Modelo de spaCy 'es_core_news_md' no encontrado.")
    print("Por favor, descárgalo ejecutando en tu terminal lo siguiente:")
    print("python -m spacy download es_core_news_md")
    nlp = None # Si no se carga, nlp será None


def encontrar_palabras_relacionadas_lista(texto: str, palabra_objetivo: str, umbral_similitud: float = 0.6) -> list[str]:
    """
    Encuentra y retorna una lista de palabras en un texto que son semánticamente
    relacionadas con una palabra o frase objetivo, usando similitud vectorial.

    Args:
        texto (str): El texto donde buscar.
        palabra_objetivo (str): La palabra o frase a buscar palabras relacionadas.
        umbral_similitud (float): El umbral de similitud coseno (entre 0 y 1).
                                   Valores más altos requieren mayor similitud.
                                   0.6 es un valor inicial razonable, pero puede requerir ajuste.

    Returns:
        list[str]: Una lista de las palabras (texto original del token) encontradas
                   en el texto que superaron el umbral de similitud con la
                   palabra objetivo. Retorna una lista vacía si no se encuentran
                   palabras relacionadas o si el modelo no está disponible/funciona.
    """
    if nlp is None:
        print("El modelo de spaCy no está disponible. No se puede procesar.")
        return [] # Retorna lista vacía si el modelo no está disponible

    # Procesar el texto y la palabra objetivo con el modelo
    doc_texto = nlp(texto)
    doc_objetivo = nlp(palabra_objetivo)

    # Verificar si la palabra objetivo tiene un vector. Si no,
    # no podemos calcular la similitud y no encontraremos nada relacionado.
    if not doc_objetivo.has_vector:
        print(f"Advertencia: La palabra o frase objetivo '{palabra_objetivo}' no tiene un vector asociado en el modelo.")
        print("Puede que sea una palabra poco común o fuera del vocabulario del modelo.")
        return [] # Retorna lista vacía si la palabra objetivo no tiene vector

    # Lista para almacenar las palabras encontradas que cumplen el criterio
    palabras_encontradas = []

    # Iterar sobre los tokens (palabras) del texto
    for token_texto in doc_texto:
        # Ignorar puntuación, espacios, y stop words
        # (las stop words rara vez serán semánticamente similares a palabras clave)
        if token_texto.is_punct or token_texto.is_space or token_texto.is_stop:
            continue

        # Verificar si el token del texto actual tiene un vector
        if not token_texto.has_vector:
            continue # Saltar palabras sin vector

        # Calcular la similitud entre el token del texto y la palabra/frase objetivo
        # spaCy permite comparar la similitud entre un Token y un Doc/Span
        similitud = token_texto.similarity(doc_objetivo)

        # Si la similitud supera el umbral, añadimos la palabra a nuestra lista
        if similitud >= umbral_similitud:
            # Añadimos el texto original del token a la lista
            palabras_encontradas.append(token_texto.text)

    # Retorna la lista completa de palabras encontradas
    return palabras_encontradas

# --- Ejemplos de Uso ---

if __name__ == "__main__":
    texto1 = "El perro corre rápido por el parque. El canino parece feliz."
    palabra1 = "perro"
    print(f"Texto: '{texto1}'")
    print(f"Palabra objetivo: '{palabra1}'")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto1, palabra1)}")
    # Esperado: ['canino'] (asumiendo que 'canino' supera el umbral con 'perro')
    print("-" * 20)

    texto2 = "El gato duerme la siesta. Es un felino perezoso."
    palabra2 = "perro"
    print(f"Texto: '{texto2}'")
    print(f"Palabra objetivo: '{palabra2}'")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto2, palabra2)}")
    # Esperado: [] (a menos que 'gato' o 'felino' tengan una similitud sorprendente alta con 'perro' en el modelo)
    print("-" * 20)

    texto3 = "Este coche es muy veloz. Me gusta el auto."
    palabra3 = "rápido"
    print(f"Texto: '{texto3}'")
    palabra3 = "rápido"
    print(f"Palabra objetivo: '{palabra3}'")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto3, palabra3)}")
    # Esperado: ['veloz'] (asumiendo que 'veloz' supera el umbral con 'rápido')
    print("-" * 20)

    texto4 = "La casa es grande y bonita."
    palabra4 = "ordenador"
    print(f"Texto: '{texto4}'")
    print(f"Palabra objetivo: '{palabra4}'")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto4, palabra4)}")
    # Esperado: []
    print("-" * 20)

    texto5 = "Compramos un automóvil nuevo. Es un gran auto."
    palabra5 = "coche"
    print(f"Texto: '{texto5}'")
    palabra5 = "coche"
    print(f"Palabra objetivo: '{palabra5}'")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto5, palabra5)}")
    # Esperado: ['automóvil', 'auto'] (asumiendo que superan el umbral)
    print("-" * 20)

    texto6 = "El pájaro vuela alto."
    palabra6 = "pez"
    print(f"Texto: '{texto6}'")
    palabra_clave6_baja = "pez"
    print(f"Palabra objetivo: '{palabra_clave6_baja}' (Umbral: 0.4)")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto6, palabra_clave6_baja, umbral_similitud=0.4)}")
    # Probablemente [] incluso con umbral bajo
    print("-" * 20)

    texto7 = "Es un perro muy grande y tiene un canino enorme y le encanta jugar con otros cachorros. Un can feliz."
    palabra7 = "perro"
    print(f"Texto: '{texto7}'")
    palabra7 = "perro"
    print(f"Palabra objetivo: '{palabra7}'")
    print(f"Palabras relacionadas encontradas: {encontrar_palabras_relacionadas_lista(texto7, palabra7)}")
    # Esperado: ['canino', 'cachorros', 'can'] (asumiendo que superan el umbral)
    print("-" * 20)