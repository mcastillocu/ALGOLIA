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
    nlp = None # Si no se carga, nlp será None


def encontrar_palabras_relacionadas(texto: str, palabra_objetivo: str, umbral_similitud: float = 0.6) -> bool:
    """
    Verifica si un texto contiene palabras semánticamente relacionadas
    con una palabra o frase objetivo, usando similitud vectorial.

    Args:
        texto (str): El texto donde buscar.
        palabra_objetivo (str): La palabra o frase a buscar palabras relacionadas.
        umbral_similitud (float): El umbral de similitud coseno (entre 0 y 1).
                                   Valores más altos requieren mayor similitud.
                                   0.6 es un valor inicial razonable, pero puede requerir ajuste.

    Returns:
        bool: True si se encuentra al menos una palabra relacionada por encima
              del umbral, False en caso contrario.
    """
    if nlp is None:
        print("El modelo de spaCy no está disponible. No se puede procesar.")
        return False

    # Procesar el texto y la palabra objetivo con el modelo
    doc_texto = nlp(texto)
    doc_objetivo = nlp(palabra_objetivo)

    # Verificar si la palabra objetivo tiene un vector. Si no,
    # no podemos calcular la similitud y no encontraremos nada relacionado.
    if not doc_objetivo.has_vector:
        print(f"Advertencia: La palabra o frase objetivo '{palabra_objetivo}' no tiene un vector asociado en el modelo.")
        print("Puede que sea una palabra poco común o fuera del vocabulario del modelo.")
        return False

    # Iterar sobre los tokens (palabras) del texto
    for token_texto in doc_texto:
        # Ignorar puntuación, espacios y quizás stop words
        # (las stop words rara vez serán semánticamente similares a palabras clave)
        if token_texto.is_punct or token_texto.is_space or token_texto.is_stop:
            continue

        # Verificar si el token del texto actual tiene un vector
        if not token_texto.has_vector:
            continue # Saltar palabras sin vector

        # Calcular la similitud entre el token del texto y la palabra/frase objetivo
        # spaCy permite comparar la similitud entre un Token y un Doc/Span
        similitud = token_texto.similarity(doc_objetivo)

        # Si la similitud supera el umbral, hemos encontrado una palabra relacionada
        if similitud >= umbral_similitud:
            # Opcional: Puedes imprimir qué palabra se encontró y su similitud
            # print(f"Encontrada palabra potencialmente relacionada: '{token_texto.text}' con '{palabra_objetivo}' (Similitud: {similitud:.2f})")
            return True # Encontramos al menos una, retornamos True inmediatamente

    # Si recorrimos todo el texto y no encontramos ninguna palabra por encima del umbral
    return False

# --- Ejemplos de Uso ---

if nlp is not None: # Solo ejecutar ejemplos si el modelo se cargó
    texto1 = "El perro corre rápido por el parque. El canino parece feliz."
    palabra1 = "perro"
    print(f"Texto: '{texto1}'")
    print(f"Palabra objetivo: '{palabra1}'")
    print(f"¿Tiene palabras relacionadas? {encontrar_palabras_relacionadas(texto1, palabra1)}") # Esperado: True (canino)
    print("-" * 20)

    texto2 = "El gato duerme la siesta. Es un felino perezoso."
    palabra2 = "perro"
    print(f"Texto: '{texto2}'")
    print(f"Palabra objetivo: '{palabra2}'")
    print(f"¿Tiene palabras relacionadas? {encontrar_palabras_relacionadas(texto2, palabra2)}") # Esperado: False (a menos que gato/felino tengan *cierta* similitud con perro en el modelo, pero probablemente baja)
    print("-" * 20)

    texto3 = "Este coche es muy veloz."
    palabra3 = "rápido"
    print(f"Texto: '{texto3}'")
    print(f"Palabra objetivo: '{palabra3}'")
    print(f"¿Tiene palabras relacionadas? {encontrar_palabras_relacionadas(texto3, palabra3)}") # Esperado: True (veloz ~ rápido)
    print("-" * 20)

    texto4 = "La casa es grande y bonita."
    palabra4 = "ordenador"
    print(f"Texto: '{texto4}'")
    print(f"Palabra objetivo: '{palabra4}'")
    print(f"¿Tiene palabras relacionadas? {encontrar_palabras_relacionadas(texto4, palabra4)}") # Esperado: False
    print("-" * 20)

    texto5 = "Compramos un automóvil nuevo."
    palabra5 = "coche"
    print(f"Texto: '{texto5}'")
    print(f"Palabra objetivo: '{palabra5}'")
    print(f"¿Tiene palabras relacionadas? {encontrar_palabras_relacionadas(texto5, palabra5)}") # Esperado: True (automóvil ~ coche)
    print("-" * 20)

    texto6 = "El pájaro vuela alto."
    palabra6 = "pez"
    # Prueba con un umbral más bajo si quieres ser menos estricto
    print(f"Texto: '{texto6}'")
    print(f"Palabra objetivo: '{palabra6}' (Umbral: 0.4)")
    print(f"¿Tiene palabras relacionadas? {encontrar_palabras_relacionadas(texto6, palabra6, umbral_similitud=0.4)}") # Probablemente False incluso con umbral bajo
    print("-" * 20)