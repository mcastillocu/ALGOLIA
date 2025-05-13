import pandas as pd
import re
import numpy as np # For np.nan

# --- Helper Functions ---

def safe_lower(text):
    if pd.isna(text) or text is None:
        return ""
    return str(text).lower()

def find_keywords_binary(text, yes_keywords, no_keywords=None, default_empty=""):
    """
    Checks for keywords to determine a 'Sí'/'No' value.
    'No' keywords take precedence if provided and found.
    """
    text_lower = safe_lower(text)
    if not text_lower:
        return default_empty

    if no_keywords:
        for keyword in no_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                return "No"
    
    for keyword in yes_keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            return "Sí"
            
    return default_empty

def find_keywords_value(text, keyword_map, default_empty=""):
    """
    Finds the first matching keyword and returns its associated value from the map.
    The keyword_map keys should be lowercase.
    """
    text_lower = safe_lower(text)
    if not text_lower:
        return default_empty
        
    for keyword, value in keyword_map.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            return value
    return default_empty

def extract_specific_value(text, patterns, default_empty=""):
    """
    Extracts a value using a list of regex patterns. Returns the first group of the first match.
    Patterns should be pre-compiled regex objects or strings.
    """
    text_str = safe_lower(text) # Use safe_lower to handle potential NaN
    if not text_str:
        return default_empty

    for pattern in patterns:
        match = re.search(pattern, text_str)
        if match:
            if match.groups(): # Check if there are any capturing groups
                return match.group(1).strip() # Return the first captured group
            else: # If no capturing groups, but pattern matches, maybe the pattern itself is the value
                return match.group(0).strip() 
    return default_empty
    
def extract_multiple_matches(text, keyword_list, unique=True, default_empty=""):
    """
    Finds all matching keywords from a list and returns them as a comma-separated string.
    Keywords in keyword_list should be lowercase.
    """
    text_lower = safe_lower(text)
    if not text_lower:
        return default_empty
        
    found_items = []
    for keyword in keyword_list:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            found_items.append(keyword.capitalize()) # Capitalize for display
            
    if unique:
        found_items = sorted(list(set(found_items)))
        
    return ", ".join(found_items) if found_items else default_empty

# --- Main Processing Function ---
def enrich_product_catalog(input_file_path, output_file_path="enriched_catalog_output.csv"):
    """
    Reads product data, enriches it with new attributes, and saves to a new CSV file.
    """
    try:
        if input_file_path.endswith('.xlsx') or input_file_path.endswith('.xls'):
            df = pd.read_excel(input_file_path)
        elif input_file_path.endswith('.csv'):
            df = pd.read_csv(input_file_path)
        else:
            print(f"Unsupported file format: {input_file_path}. Please use .csv or .xlsx.")
            return
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Define new column names in order
    new_column_names = [
        "Tono / Color", "Acabado", "Cobertura", "Formato cosmético", "Función / Beneficio",
        "Duración / Resistencia al agua", "Con fragancia (Sí / No)", "Con protección solar (Sí / No)",
        "FPS", "Ingredientes activos", "Edad recomendada / Etapa bebé", "Formato bebé",
        "Hipoalergénico / Dermatológicamente probado (Sí / No)", "Con ingredientes naturales (Sí / No)",
        "Sin conservantes (Sí / No)", "Material / Textura bebé", 
        "Antiderrames / Anticólicos / Antibacteriano (Sí / No)", "Con BPA (Sí / No)",
        "Compatible con esterilizadores (Sí / No)", "Facilidad de digestión (Sí / No / Alta / Media / Baja)",
        "Con alcohol (Sí / No)", "Protección 24h / Resistente al agua (Sí / No)",
        "Formato dermocosmético", "Con color (Sí / No)", "Zonas de uso", "Libre de alcohol (Sí / No)",
        "Libre de aceites (Sí / No)", "Libre de parabenos (Sí / No)", "Libre de comedogénicos (Sí / No)",
        "Con enjuague (Sí / No)", "Orgánico (Sí / No)", "Natural (Sí / No)", "Sin aditivos (Sí / No)",
        "Vegetariano (Sí / No)", "Keto (Sí / No)", "Bajo en sodio (Sí / No)", "Fuente de proteína (Sí / No)",
        "Fuente de fibra (Sí / No)", "Fuente de vitaminas (Sí / No)", "Apto para diabéticos (Sí / No)",
        "Apto para celíacos (Sí / No)", "Con edulcorantes naturales (Sí / No)",
        "Con edulcorantes artificiales (Sí / No)", "Función hogar", "Fragancia hogar",
        "Biodegradable (Sí / No)", "Reutilizable (Sí / No)",
        "Compatible con lavavajillas / microondas / mascotas / superficies",
        "Durabilidad / Resistencia", "Uso (Interior / Exterior)", "Sabor o aroma (para mascotas o alimentos)",
        "Beneficio para mascotas", "Tipo de suplemento", "Objetivo / Beneficio deportivo",
        "Sabor deportivo", "Presentación suplemento", "Con cafeína (Sí / No)", "Sin lactosa (Sí / No)",
        "Certificaciones", "Forma de consumo", "Incluye accesorios (Sí / No)", "Tipo de deporte",
        "Compatibilidad con apps, máquinas o rutinas (Sí / No)"
    ]

    # Initialize new columns with a default empty value (NaN which becomes empty in CSV)
    for col_name in new_column_names:
        df[col_name] = np.nan # Using np.nan for better handling, will be empty in CSV

    # Pre-compile regex patterns for performance
    fps_patterns = [
        re.compile(r'fps\s*(\d+\+?(?:-\d+)?)', re.IGNORECASE),
        re.compile(r'spf\s*(\d+\+?(?:-\d+)?)', re.IGNORECASE),
        re.compile(r'protección\s*uv\s*(\d+\+?)', re.IGNORECASE),
        re.compile(r'uv\s*(\d+\+?)', re.IGNORECASE),
        re.compile(r'factor\s*de\s*protección\s*solar\s*(\d+)', re.IGNORECASE)
    ]
    
    color_patterns = [
        # Basic color names
        re.compile(r'\b(rojo|azul|verde|amarillo|negro|blanco|rosa|morado|naranja|marrón|gris|beige|dorado|plateado|bronce|cobre|lila|turquesa|fucsia|coral|vino|oliva|nude|transparente)\b', re.IGNORECASE),
        # Tono/Color followed by a name or number
        re.compile(r'\b(?:tono|color|shade)\s*:?\s*([a-z0-9\s\-#]+?)(?:\s*\||\s*//|\s*\n|\s*$|\b(?:claro|medio|oscuro)\b)', re.IGNORECASE),
        re.compile(r'\b([a-z\s]+)\s*(?:claro|medio|oscuro)\b', re.IGNORECASE), # e.g., "rojo claro"
        re.compile(r'#([a-f0-9]{6}|[a-f0-9]{3})\b', re.IGNORECASE), # Hex codes
        re.compile(r'\b\d{2,4}\s*([a-zA-Z\s]+)\b'), # e.g. "102 Light Beige" - extract "Light Beige"
        re.compile(r'\b([a-zA-Z\-]+)\s*\d{2,4}\b') # e.g. "Nude 200" - extract "Nude"
    ]


    # --- Keyword Dictionaries and Lists (examples, expand significantly) ---
    acabado_map = {"mate": "Mate", "matte": "Mate", "brillante": "Brillante", "shimmer": "Brillante", "glow": "Brillante", "luminoso": "Brillante", "satinado": "Satinado", "satin": "Satinado", "natural": "Natural", "velvet":"Satinado", "efecto polvo":"Mate"}
    cobertura_map = {"ligera": "Ligera", "sheer": "Ligera", "baja":"Ligera", "media": "Media", "medium": "Media", "alta": "Alta", "full coverage": "Alta", "total":"Alta"}
    formato_cosmetico_map = {"líquido": "Líquido", "liquid": "Líquido", "barra": "Barra", "stick": "Barra", "polvo": "Polvo", "powder": "Polvo", "crema": "Crema", "cream": "Crema", "gel": "Gel", "lápiz": "Lápiz", "pencil": "Lápiz", "serum":"Suero", "aceite":"Aceite", "balsamo":"Bálsamo", "mousse":"Mousse", "spray":"Spray", "bruma":"Spray", "mist":"Spray"}
    
    funcion_beneficio_keywords = [
        "hidratación", "hidratante", "humectante", "nutrición", "nutritivo", "anti-edad", "antiedad", "antiage", "anti-arrugas",
        "reafirmante", "lifting", "volumen", "voluminizador", "definición", "definidor", "control caída", "anti caída",
        "anti-caspa", "anticaspa", "anti-frizz", "antifrizz", "alisante", "liso perfecto", "protección color", "reparador",
        "fortalecedor", "brillo", "iluminador", "matificante", "control grasa", "limpieza profunda", "purificante",
        "calmante", "suavizante", "anti-imperfecciones", "corrector", "despigmentante", "aclarante", "exfoliante",
        "refrescante", "energizante", "revitalizante", "detox", "protector térmico", "protector uv"
    ]
    
    ingredientes_activos_list = [
        "ácido hialurónico", "hialuronato de sodio", "retinol", "retinal", "vitamina c", "ácido ascórbico", "niacinamida", "vitamina b3",
        "ácido salicílico", "bha", "ácido glicólico", "aha", "ceramidas", "péptidos", "colágeno", "aloe vera",
        "árbol de té", "tea tree", "centella asiática", "madecassoside", "escualano", "pantenol", "vitamina b5",
        "vitamina e", "tocoferol", "cafeína", "extracto de té verde", "extracto de manzanilla", "karité", "aceite de argán",
        "aceite de jojoba", "aceite de coco", "ácido láctico", "urea", "glicerina", "probióticos", "prebióticos",
        "resveratrol", "ácido ferúlico", "bakuchiol", "zinc pca", "azufre", "arcilla"
    ]
    
    formato_bebe_map = {"líquido": "Líquido", "polvo": "Polvo", "crema": "Crema", "toallita": "Toallita", "toallitas":"Toallita", "gel":"Gel", "aceite":"Aceite", "bálsamo":"Bálsamo", "spray":"Spray", "shampoo":"Líquido", "jabón":"Barra/Líquido"} # Jabon might be tricky
    
    zonas_uso_keywords = {"cara":"Cara", "rostro":"Cara", "cuerpo":"Cuerpo", "cabello":"Cuero cabelludo/Cabello", "cuero cabelludo":"Cuero cabelludo", "ojos":"Ojos", "contorno de ojos":"Ojos", "labios":"Labios", "manos":"Manos", "pies":"Pies", "uñas":"Uñas", "zona íntima":"Zona íntima", "axilas":"Cuerpo"}

    # --- Iterate over rows ---
    for index, row in df.iterrows():
        # Ensure all relevant input columns are strings and lowercase
        # Use .get(col, '') to handle potentially missing columns in the input file gracefully
        descripcion = safe_lower(row.get('Descripción Item', ''))
        division = safe_lower(row.get('División', ''))
        sub_clase = safe_lower(row.get('Sub-Clase', ''))
        marca = safe_lower(row.get('Marca', ''))
        presentacion = safe_lower(row.get('Presentación del Producto', ''))
        
        # Existing enriched columns (ensure they are read correctly)
        etapa_bebe_val = safe_lower(row.get('Etapa', '')) # 'Etapa' column from input
        tipo_piel_val = safe_lower(row.get('Tipo de piel', ''))
        tipo_cabello_val = safe_lower(row.get('Tipo de cabello', ''))
        gluten_free_val = safe_lower(row.get('Gluten Free', '')) # 'Gluten Free' column from input
        vegan_val = safe_lower(row.get('Vegan', ''))
        sugar_free_val = safe_lower(row.get('Sugar Free', ''))

        # Combine relevant text fields for broader searching
        full_text = f"{descripcion} {division} {sub_clase} {marca} {presentacion}"

        # --- Attribute Extraction Logic (examples, needs significant expansion) ---

        # 1. Tono / Color
        extracted_color = extract_specific_value(descripcion, color_patterns) # Prioritize description
        if not extracted_color:
             extracted_color = extract_specific_value(sub_clase, color_patterns) # Fallback to sub_clase
        df.loc[index, "Tono / Color"] = extracted_color
        
        # 2. Acabado
        df.loc[index, "Acabado"] = find_keywords_value(full_text, acabado_map)

        # 3. Cobertura
        df.loc[index, "Cobertura"] = find_keywords_value(full_text, cobertura_map)

        # 4. Formato cosmético
        # Prioritize 'Presentación del Producto', then keywords in full_text
        fmt_cosmetico = formato_cosmetico_map.get(presentacion, "")
        if not fmt_cosmetico:
            fmt_cosmetico = find_keywords_value(full_text, formato_cosmetico_map)
        df.loc[index, "Formato cosmético"] = fmt_cosmetico

        # 5. Función / Beneficio
        df.loc[index, "Función / Beneficio"] = extract_multiple_matches(full_text, funcion_beneficio_keywords)

        # 6. Duración / Resistencia al agua
        dur_res_keywords = ["larga duración", "24h", "12h", "8h", "waterproof", "resistente al agua", "a prueba de agua", "sweatproof", "sweat resistant"]
        df.loc[index, "Duración / Resistencia al agua"] = extract_multiple_matches(full_text, dur_res_keywords)

        # 7. Con fragancia (Sí / No)
        frag_yes_kw = ["fragancia", "perfumado", "aroma", "perfume"]
        frag_no_kw = ["sin fragancia", "sin perfume", "fragrance-free", "no perfumado", "unscented"]
        df.loc[index, "Con fragancia (Sí / No)"] = find_keywords_binary(full_text, frag_yes_kw, frag_no_kw)

        # 8. Con protección solar (Sí / No)
        spf_keywords_yes = ["spf", "fps", "protección solar", "filtro solar", "uv protection", "bloqueador solar", "sunscreen"]
        df.loc[index, "Con protección solar (Sí / No)"] = find_keywords_binary(full_text, spf_keywords_yes)

        # 9. FPS
        df.loc[index, "FPS"] = extract_specific_value(full_text, fps_patterns)

        # 10. Ingredientes activos
        df.loc[index, "Ingredientes activos"] = extract_multiple_matches(descripcion, ingredientes_activos_list) # Focus on description for ingredients

        # 11. Edad recomendada / Etapa bebé
        if etapa_bebe_val == "bebé": # Check the existing 'Etapa' column
            edad_bebe_patterns = [
                re.compile(r'(\d+\s*-\s*\d+\s*meses)', re.IGNORECASE),
                re.compile(r'(\d+\+?\s*meses)', re.IGNORECASE),
                re.compile(r'(recién nacido)', re.IGNORECASE),
                re.compile(r'(etapa\s*\d+)', re.IGNORECASE),
                re.compile(r'(\d+\s*a\s*\d+\s*años)', re.IGNORECASE) # For older babies/toddlers
            ]
            df.loc[index, "Edad recomendada / Etapa bebé"] = extract_specific_value(full_text, edad_bebe_patterns)
        
        # 12. Formato bebé
        if etapa_bebe_val == "bebé":
            fmt_bebe = formato_bebe_map.get(presentacion, "")
            if not fmt_bebe:
                 fmt_bebe = find_keywords_value(full_text, formato_bebe_map)
            df.loc[index, "Formato bebé"] = fmt_bebe

        # 13. Hipoalergénico / Dermatológicamente probado (Sí / No)
        hipo_derma_kw = ["hipoalergénico", "dermatológicamente probado", "testeado dermatologicamente", "probado por dermatólogos", "piel sensible"] # piel sensible can be a strong hint
        df.loc[index, "Hipoalergénico / Dermatológicamente probado (Sí / No)"] = find_keywords_binary(full_text, hipo_derma_kw)

        # 14. Con ingredientes naturales (Sí / No) (See also #32 Natural)
        ing_nat_yes_kw = ["ingredientes naturales", "extractos naturales", "origen natural", "100% natural", "90% natural"] # e.g., "90% ingredientes naturales"
        ing_nat_no_kw = ["sin ingredientes naturales"] # Less common
        df.loc[index, "Con ingredientes naturales (Sí / No)"] = find_keywords_binary(full_text, ing_nat_yes_kw, ing_nat_no_kw)

        # 15. Sin conservantes (Sí / No)
        df.loc[index, "Sin conservantes (Sí / No)"] = find_keywords_binary(full_text, ["sin conservantes", "libre de conservantes", "no conservatives", "preservative-free"], ["con conservantes"])

        # 16. Material / Textura bebé
        if etapa_bebe_val == "bebé":
            mat_tex_bebe_kw = ["suave", "extrasuave", "algodón", "cotton", "orgánico algodón", "bambú", "tela", "textura delicada", "biodegradable"] # Biodegradable can be material aspect for wipes
            df.loc[index, "Material / Textura bebé"] = extract_multiple_matches(full_text, mat_tex_bebe_kw)
        
        # 17. Antiderrames / Anticólicos / Antibacteriano (Sí / No)
        anti_x_kw = ["antiderrames", "anti derrames", "no spill", "anticólicos", "anti cólicos", "anti-colic", "antibacteriano", "anti bacterial", "anti-bacterial"]
        df.loc[index, "Antiderrames / Anticólicos / Antibacteriano (Sí / No)"] = find_keywords_binary(full_text, anti_x_kw)

        # 18. Con BPA (Sí / No)
        df.loc[index, "Con BPA (Sí / No)"] = find_keywords_binary(full_text, ["con bpa"], ["sin bpa", "libre de bpa", "bpa free", "0% bpa"])
        
        # 19. Compatible con esterilizadores (Sí / No)
        esterilizador_kw = ["apto para esterilizador", "esterilizable", "compatible con esterilizador"]
        df.loc[index, "Compatible con esterilizadores (Sí / No)"] = find_keywords_binary(full_text, esterilizador_kw)

        # 20. Facilidad de digestión (Sí / No / Alta / Media / Baja)
        # This is complex. Let's simplify to Yes/No for now, or specific keywords.
        facil_dig_map = {
            "fácil digestión": "Sí/Alta", "digestión suave": "Sí/Alta", "alta digestibilidad": "Alta",
            "digestión ligera": "Sí/Alta", "gentle digestion":"Sí/Alta"
        }
        df.loc[index, "Facilidad de digestión (Sí / No / Alta / Media / Baja)"] = find_keywords_value(full_text, facil_dig_map)

        # 21. Con alcohol (Sí / No) (Attribute 26 is "Libre de alcohol")
        # If "Libre de alcohol" is "Sí", then this should be "No".
        # Explicit "con alcohol" or "alcohol denat." means "Sí".
        # If "Libre de alcohol" is "No" or empty, and "con alcohol" isn't found, this is ambiguous.
        if find_keywords_binary(full_text, ["sin alcohol", "libre de alcohol", "alcohol-free", "0% alcohol"]) == "Sí":
            df.loc[index, "Con alcohol (Sí / No)"] = "No"
        elif find_keywords_binary(full_text, ["alcohol", "alcohol denat"]) == "Sí": # Check this only if not "libre de alcohol"
             # Be careful: "alcohol cetílico" is different. Need more context for general "alcohol".
             # For now, if "alcohol denat." or "alcohol etílico" it's Yes. If just "alcohol", it's ambiguous.
            if "alcohol denat" in full_text or "alcohol etilico" in full_text or "ethyl alcohol" in full_text:
                 df.loc[index, "Con alcohol (Sí / No)"] = "Sí"
            # else leave empty or set based on other rules. For now, simple check.

        # 22. Protección 24h / Resistente al agua (Sí / No) (Similar to #6)
        # Combine keywords from #6 for "Resistente al agua" part. Add "24h", "protección duradera".
        prot_24h_resist_kw = ["24h", "12h", "larga duración", "waterproof", "resistente al agua", "a prueba de agua", "protección prolongada"]
        df.loc[index, "Protección 24h / Resistente al agua (Sí / No)"] = find_keywords_binary(full_text, prot_24h_resist_kw)

        # 23. Formato dermocosmético
        # Same as formato_cosmetico_map, but maybe only apply if 'dermocosmeticos' in division/sub_clase
        if "dermocosmetico" in division or "dermocosmetico" in sub_clase:
            fmt_dermo = formato_cosmetico_map.get(presentacion, "") # Use same map
            if not fmt_dermo:
                fmt_dermo = find_keywords_value(full_text, formato_cosmetico_map)
            df.loc[index, "Formato dermocosmético"] = fmt_dermo
        
        # 24. Con color (Sí / No)
        # If Tono/Color is filled, then "Sí". Or keywords like "con color", "tinted".
        if pd.notna(df.loc[index, "Tono / Color"]) and df.loc[index, "Tono / Color"] != "":
            df.loc[index, "Con color (Sí / No)"] = "Sí"
        else:
            df.loc[index, "Con color (Sí / No)"] = find_keywords_binary(full_text, ["con color", "tinted", "bb cream", "cc cream"], ["sin color", "transparente", "incoloro"])

        # 25. Zonas de uso
        df.loc[index, "Zonas de uso"] = extract_multiple_matches(full_text, list(zonas_uso_keywords.keys()))


        # 26. Libre de alcohol (Sí / No)
        df.loc[index, "Libre de alcohol (Sí / No)"] = find_keywords_binary(full_text, ["sin alcohol", "libre de alcohol", "alcohol-free", "0% alcohol"], ["con alcohol", "alcohol denat"])
        # Update #21 based on this
        if df.loc[index, "Libre de alcohol (Sí / No)"] == "Sí":
            df.loc[index, "Con alcohol (Sí / No)"] = "No"
        elif df.loc[index, "Libre de alcohol (Sí / No)"] == "No": # Means it DOES contain alcohol
            df.loc[index, "Con alcohol (Sí / No)"] = "Sí"


        # 27. Libre de aceites (Sí / No)
        df.loc[index, "Libre de aceites (Sí / No)"] = find_keywords_binary(full_text, ["sin aceite", "libre de aceite", "oil-free", "oil free", "no graso"], ["con aceite"])

        # 28. Libre de parabenos (Sí / No)
        df.loc[index, "Libre de parabenos (Sí / No)"] = find_keywords_binary(full_text, ["sin parabenos", "libre de parabenos", "paraben-free", "paraben free"], ["con parabenos"])

        # 29. Libre de comedogénicos (Sí / No)
        df.loc[index, "Libre de comedogénicos (Sí / No)"] = find_keywords_binary(full_text, ["no comedogénico", "non-comedogenic", "libre de comedogenicos"], ["comedogénico"])

        # 30. Con enjuague (Sí / No)
        df.loc[index, "Con enjuague (Sí / No)"] = find_keywords_binary(full_text, ["con enjuague", "enjuagar", "rinse-off", "aclarar"], ["sin enjuague", "leave-in", "no rinse", "no aclarar"])

        # --- Food/Supplements/General Claims ---
        # 31. Orgánico (Sí / No)
        df.loc[index, "Orgánico (Sí / No)"] = find_keywords_binary(full_text, ["orgánico", "organic", "bio", "ecológico"], ["no orgánico"])

        # 32. Natural (Sí / No) (Can overlap with #14)
        # If #14 is "Sí", this can also be "Sí".
        if df.loc[index, "Con ingredientes naturales (Sí / No)"] == "Sí":
            df.loc[index, "Natural (Sí / No)"] = "Sí"
        else:
            df.loc[index, "Natural (Sí / No)"] = find_keywords_binary(full_text, ["natural", "100% natural", "totalmente natural"], ["artificial", "sintético"])
        
        # 33. Sin aditivos (Sí / No)
        df.loc[index, "Sin aditivos (Sí / No)"] = find_keywords_binary(full_text, ["sin aditivos", "sin colorantes artificiales", "sin saborizantes artificiales", "sin conservadores artificiales"], ["con aditivos"])

        # 34. Vegetariano (Sí / No)
        # If Vegan (from input) is Yes, then Vegetariano is Yes.
        if vegan_val == "sí": # Assuming input 'Vegan' is "Sí" or "No"
            df.loc[index, "Vegetariano (Sí / No)"] = "Sí"
        else:
            df.loc[index, "Vegetariano (Sí / No)"] = find_keywords_binary(full_text, ["vegetariano", "vegetarian", "apto para vegetarianos", "veggie"], ["no vegetariano"])
        
        # 35. Keto (Sí / No)
        df.loc[index, "Keto (Sí / No)"] = find_keywords_binary(full_text, ["keto", "cetogénico", "keto friendly"])

        # 36. Bajo en sodio (Sí / No)
        df.loc[index, "Bajo en sodio (Sí / No)"] = find_keywords_binary(full_text, ["bajo en sodio", "low sodium", "reducido en sodio", "sin sal añadida"])

        # 37. Fuente de proteína (Sí / No)
        df.loc[index, "Fuente de proteína (Sí / No)"] = find_keywords_binary(full_text, ["proteína", "protein", "alto en proteína", "fuente de proteína"])

        # 38. Fuente de fibra (Sí / No)
        df.loc[index, "Fuente de fibra (Sí / No)"] = find_keywords_binary(full_text, ["fibra", "fiber", "alto en fibra", "fuente de fibra"])

        # 39. Fuente de vitaminas (Sí / No)
        df.loc[index, "Fuente de vitaminas (Sí / No)"] = find_keywords_binary(full_text, ["vitaminas", "vitamins", "con vitaminas", "fuente de vitaminas", "multivitamínico"])

        # 40. Apto para diabéticos (Sí / No)
        df.loc[index, "Apto para diabéticos (Sí / No)"] = find_keywords_binary(full_text, ["apto para diabéticos", "diabeticos", "diabetic friendly", "sin azúcar"]) # "sin azúcar" is a strong hint

        # 41. Apto para celíacos (Sí / No)
        # Use existing 'Gluten Free' column
        if gluten_free_val == "sí": # Assuming input 'Gluten Free' is "Sí" or "No"
             df.loc[index, "Apto para celíacos (Sí / No)"] = "Sí"
        else:
             df.loc[index, "Apto para celíacos (Sí / No)"] = find_keywords_binary(full_text, ["apto para celíacos", "celiacos", "sin tacc", "gluten free"]) # Redundant but confirmatory
        
        # 42. Con edulcorantes naturales (Sí / No)
        edulc_nat_kw = ["stevia", "fruto del monje", "monk fruit", "eritritol", "xilitol", "taumatina", "edulcorante natural"]
        df.loc[index, "Con edulcorantes naturales (Sí / No)"] = find_keywords_binary(full_text, edulc_nat_kw)

        # 43. Con edulcorantes artificiales (Sí / No)
        edulc_art_kw = ["sucralosa", "aspartamo", "sacarina", "acesulfamo k", "acesulfame potassium", "ciclamato", "edulcorante artificial"]
        df.loc[index, "Con edulcorantes artificiales (Sí / No)"] = find_keywords_binary(full_text, edulc_art_kw)
        
        # --- Home Products ---
        # 44. Función hogar
        func_hogar_kw = ["limpiador", "desinfectante", "antibacterial", "multiusos", "quitamanchas", "blanqueador", "desengrasante", "ambientador", "insecticida", "abrillantador", "detergente", "suavizante"]
        df.loc[index, "Función hogar"] = extract_multiple_matches(full_text, func_hogar_kw)

        # 45. Fragancia hogar
        frag_hogar_patterns = [
            re.compile(r'\b(?:fragancia|aroma|olor)\s*(?:a\s*)?([a-z\s]+)(?:\s*\,|\s*\n|\s*$)', re.IGNORECASE),
            re.compile(r'\b(lavanda|vainilla|cítrico|floral|fresco|manzana|canela|sin olor|neutro)\b', re.IGNORECASE)
        ]
        if "hogar" in division or "limpieza" in division or "ambientador" in sub_clase:
            df.loc[index, "Fragancia hogar"] = extract_specific_value(full_text, frag_hogar_patterns)

        # 46. Biodegradable (Sí / No)
        df.loc[index, "Biodegradable (Sí / No)"] = find_keywords_binary(full_text, ["biodegradable", "compostable", "eco friendly"])

        # 47. Reutilizable (Sí / No)
        df.loc[index, "Reutilizable (Sí / No)"] = find_keywords_binary(full_text, ["reutilizable", "lavable y reutilizable", "rellenable", "refill"])

        # 48. Compatible con lavavajillas / microondas / mascotas / superficies
        compat_keywords = []
        if find_keywords_binary(full_text, ["apto lavavajillas", "dishwasher safe"]) == "Sí": compat_keywords.append("Lavavajillas")
        if find_keywords_binary(full_text, ["apto microondas", "microwave safe"]) == "Sí": compat_keywords.append("Microondas")
        if find_keywords_binary(full_text, ["seguro para mascotas", "pet safe"]) == "Sí": compat_keywords.append("Mascotas")
        if find_keywords_binary(full_text, ["multisuperficies", "todas las superficies"]) == "Sí": compat_keywords.append("Superficies")
        df.loc[index, "Compatible con lavavajillas / microondas / mascotas / superficies"] = ", ".join(compat_keywords) if compat_keywords else ""


        # 49. Durabilidad / Resistencia (Alta / Media / Baja)
        dur_map = {"alta resistencia": "Alta", "uso rudo": "Alta", "heavy duty": "Alta", "duradero": "Alta/Media", "resistente": "Media"}
        df.loc[index, "Durabilidad / Resistencia"] = find_keywords_value(full_text, dur_map)

        # 50. Uso (Interior / Exterior)
        uso_map = {"interior": "Interior", "exterior": "Exterior", "indoor": "Interior", "outdoor": "Exterior", "interior y exterior":"Interior/Exterior", "indoor/outdoor":"Interior/Exterior"}
        df.loc[index, "Uso (Interior / Exterior)"] = find_keywords_value(full_text, uso_map)

        # --- Pets / Food / Supplements (some overlap, refine by division/sub_clase) ---
        # 51. Sabor o aroma (para mascotas o alimentos)
        sabor_aroma_patterns = [
            re.compile(r'\b(?:sabor|aroma)\s*(?:a\s*)?([a-z\s&]+?)(?:\s*\,|\s*\n|\s*$|\()', re.IGNORECASE), # Sabor X, Sabor a X
             # Common flavors
            re.compile(r'\b(vainilla|chocolate|fresa|frutilla|menta|limón|naranja|manzana|pollo|carne|res|salmón|pavo|cordero|atún|buey|hígado|vegetales|cereales|frutos rojos|tropical|neutro|sin sabor)\b', re.IGNORECASE)
        ]
        if "alimentos" in division or "mascotas" in division or "suplementos" in division:
            df.loc[index, "Sabor o aroma (para mascotas o alimentos)"] = extract_specific_value(full_text, sabor_aroma_patterns)
        
        # 52. Beneficio para mascotas
        if "mascotas" in division:
            benef_masc_kw = ["digestión", "pelaje", "pelo brillante", "articulaciones", "dental", "control de peso", "energía", "vitalidad", "sistema inmune", "urinario", "sensible"]
            df.loc[index, "Beneficio para mascotas"] = extract_multiple_matches(full_text, benef_masc_kw)

        # 53. Tipo de suplemento
        tipo_supl_kw = ["proteína", "protein whey", "caseína", "aislado de proteina", "hidrolizado de proteina", "vegan protein", 
                        "creatina", "monohidrato de creatina", "bcaa", "aminoácidos", "glutamina", "pre-entreno", "pre workout",
                        "quemador de grasa", "fat burner", "termogénico", "colágeno", "omega 3", "multivitamínico", "minerales",
                        "probióticos", "fibra", "ganador de peso", "mass gainer"]
        if "suplementos" in division or "nutricion deportiva" in sub_clase:
             df.loc[index, "Tipo de suplemento"] = extract_multiple_matches(full_text, tipo_supl_kw)

        # 54. Objetivo / Beneficio deportivo
        if "suplementos" in division or "nutricion deportiva" in sub_clase:
            obj_deportivo_kw = ["energía", "rendimiento", "masa muscular", "aumento muscular", "recuperación", "fuerza", "resistencia", "pérdida de peso", "definición muscular", "hidratación deportiva", "enfoque mental"]
            df.loc[index, "Objetivo / Beneficio deportivo"] = extract_multiple_matches(full_text, obj_deportivo_kw)

        # 55. Sabor deportivo (Same as #51, but can be context-specific)
        if "suplementos" in division or "nutricion deportiva" in sub_clase:
            df.loc[index, "Sabor deportivo"] = df.loc[index, "Sabor o aroma (para mascotas o alimentos)"] # Reuse from #51 if already populated

        # 56. Presentación suplemento
        if "suplementos" in division or "nutricion deportiva" in sub_clase:
            pres_supl_map = {
                "polvo": "Polvo", "powder": "Polvo", "cápsulas": "Cápsulas", "caps": "Cápsulas", "tabletas": "Tabletas", "tabs": "Tabletas",
                "líquido": "Líquido", "liquid": "Líquido", "gomitas": "Gomitas", "gummies": "Gomitas", "shot": "Shots", "barras": "Barras", "bar": "Barras", "gel bebible":"Gel"
            }
            fmt_supl = pres_supl_map.get(presentacion, "")
            if not fmt_supl:
                 fmt_supl = find_keywords_value(full_text, pres_supl_map)
            df.loc[index, "Presentación suplemento"] = fmt_supl

        # 57. Con cafeína (Sí / No)
        df.loc[index, "Con cafeína (Sí / No)"] = find_keywords_binary(full_text, ["cafeína", "caffeine", "guaraná", "extracto de te verde"], ["sin cafeína", "decaf", "descafeinado"])

        # 58. Sin lactosa (Sí / No)
        df.loc[index, "Sin lactosa (Sí / No)"] = find_keywords_binary(full_text, ["sin lactosa", "lactose-free", "deslactosado", "0% lactosa"], ["con lactosa"])

        # 59. Certificaciones
        cert_kw = ["gmp", "fda approved", "certificado orgánico", "usda organic", "non-gmo", "iso \d+", "halal", "kosher", "fair trade", "rainforest alliance", "cruelty-free", "leaping bunny"] # Leaping bunny is also vegan related
        df.loc[index, "Certificaciones"] = extract_multiple_matches(full_text, cert_kw)

        # 60. Forma de consumo
        forma_cons_map = {
            "masticable": "Masticable", "chewable": "Masticable", "diluir en agua": "Diluido", "mezclar con líquido": "Diluido",
            "tomar directo": "Directo", "sublingual": "Sublingual", "con comidas": "Con comidas"
        }
        df.loc[index, "Forma de consumo"] = find_keywords_value(full_text, forma_cons_map)

        # 61. Incluye accesorios (Sí / No)
        df.loc[index, "Incluye accesorios (Sí / No)"] = find_keywords_binary(full_text, ["incluye \w+", "con \w+", "viene con \w+", "kit", "set de", "pack con"], ["no incluye accesorios", "accesorio se vende por separado"]) # Needs careful keyword choices for positive

        # 62. Tipo de deporte
        if "deportes" in division or "accesorios deportivos" in sub_clase or "suplementos" in division:
            tipo_deporte_kw = ["gimnasio", "gym", "fitness", "running", "correr", "ciclismo", "bicicleta", "natación", "nadar", "yoga", "pilates", "fútbol", "basketball", "tenis", "boxeo", "crossfit", "senderismo", "montañismo"]
            df.loc[index, "Tipo de deporte"] = extract_multiple_matches(full_text, tipo_deporte_kw)

        # 63. Compatibilidad con apps, máquinas o rutinas (Sí / No)
        df.loc[index, "Compatibilidad con apps, máquinas o rutinas (Sí / No)"] = find_keywords_binary(full_text, ["bluetooth", "compatible con app", "conectividad", "smart", "se integra con", "compatible con \w+ machine"])


    # Save the enriched DataFrame
    try:
        df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        print(f"Enriched catalog saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving output file: {e}")

# --- Example Usage ---
if __name__ == '__main__':
    # Create a dummy input file for testing if it doesn't exist
    # In a real scenario, replace 'dummy_input_catalog.csv' with your actual file path.
    
    dummy_data = {
        'Item': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016],
        'Código de Barras': [f'75000{i:07d}' for i in range(16)],
        'Descripción Item': [
            "Base de Maquillaje Fluida Mate Tono Beige Claro SPF15 Larga Duración 30ml", # Cosmético
            "Crema Hidratante Facial con Ácido Hialurónico y Vitamina C Anti-Edad Piel Sensible 50g Sin Fragancia", # Dermocosmético
            "Shampoo Reparador Cabello Dañado con Aceite de Argán y Keratina Sin Parabenos 400ml", # Cabello
            "Pañales Bebé Etapa 3 (6-10kg) Algodón Suave Hipoalergénicos 50 unidades", # Bebé
            "Proteína Whey Polvo Sabor Chocolate Suizo 1kg para Masa Muscular Sin Lactosa", # Suplemento
            "Limpiador Multiusos Desinfectante Hogar Aroma Lavanda Biodegradable 1L", # Hogar
            "Alimento Seco para Perro Adulto Sabor Pollo y Vegetales Digestión Saludable 3kg", # Mascotas
            "Labial Líquido Rojo Pasión Acabado Brillante Waterproof", # Cosmético
            "Suero Facial con Retinol y Niacinamida para Manchas y Arrugas 30ml Dermocosmético", # Dermocosmético
            "Toallitas Húmedas Bebé con Aloe Vera Sin Alcohol ni Perfume 80 und", # Bebé
            "Galletas Orgánicas Veganas Sin Gluten y Sin Azúcar Sabor Manzana y Canela 150g", # Alimentos
            "Bloqueador Solar Corporal SPF 50+ Resistente al Agua para Piel Sensible 200ml", # Protección Solar
            "Pre-entreno Energizante con Cafeína y BCAA Sabor Frutos Rojos 300g", # Suplemento deportivo
            "Biberón Anticólicos Bebé 0-6 Meses Sin BPA Compatible con Esterilizador 150ml", # Bebé Accesorios
            "Detergente Líquido Ropa Delicada Hipoalergénico Sin Fosfatos 2L", # Hogar
            "Juguete Interactivo para Gato con Plumas y Catnip Reutilizable" # Mascotas Accesorios
        ],
        'División': [
            "MAQUILLAJE", "CUIDADO FACIAL", "CUIDADO CAPILAR", "BEBE", 
            "SUPLEMENTOS", "LIMPIEZA HOGAR", "MASCOTAS", "MAQUILLAJE",
            "DERMOCOSMETICOS", "BEBE", "ALIMENTOS SALUDABLES", "CUIDADO CORPORAL",
            "NUTRICION DEPORTIVA", "BEBE ACCESORIOS", "LIMPIEZA ROPA", "MASCOTAS JUGUETES"
        ],
        'Sub-Clase': [
            "BASES FLUIDAS", "HIDRATANTES ANTIEDAD", "SHAMPOOS TRATANTES", "PAÑALES DESECHABLES",
            "PROTEINAS", "LIMPIADORES MULTIUSOS", "ALIMENTO SECO PERRO", "LABIALES LIQUIDOS",
            "SERUMS FACIALES", "TOALLITAS HUMEDAS", "GALLETAS ORGANICAS", "PROTECTORES SOLARES",
            "PRE-ENTRENOS", "BIBERONES", "DETERGENTES LIQUIDOS", "JUGUETES GATO"
        ],
        'Marca': [
            "LuxeCosmetics", "DermaCare", "HairRevive", "BabySoft", "MuscleUp", "CleanHome", "Pet радостен",
            "GlamLips", "SkinPerfect", "GentleWipes", "PureBites", "SunGuard", "XtremeFuel", "NurtureFeed",
            "SoftWash", "PlayfulPaws"
        ],
        'Contenido Neto': [30, 50, 400, 50, 1, 1, 3, 5, 30, 80, 150, 200, 300, 150, 2, 1],
        'Unidad de Medida': ["ml", "g", "ml", "unidades", "kg", "L", "kg", "ml", "ml", "und", "g", "ml", "g", "ml", "L", "unidad"],
        'Presentación del Producto': [
            "Frasco", "Pote", "Botella", "Paquete", "Bolsa", "Botella", "Bolsa", "Tubo", "Frasco con gotero",
            "Paquete", "Caja", "Tubo", "Pote", "Caja", "Botella", "Blister"
        ],
        'Vegan': ["No", "Sí", "No", "No", "No", "Sí", "No", "Sí", "Sí", "Sí", "Sí", "No", "Sí", "No", "Sí", "No"],
        'Gluten Free': ["No", "Sí", "Sí", "Sí", "No", "Sí", "No", "Sí", "Sí", "Sí", "Sí", "Sí", "No", "Sí", "Sí", "Sí"],
        'Sugar Free': ["No", "Sí", "No", "Sí", "Sí", "Sí", "No", "No", "Sí", "Sí", "Sí", "Sí", "No", "Sí", "Sí", "Sí"],
        'Talla': ["30 ml", "50 g", "400 ml", "50 unidades", "1 kg", "1 L", "3 kg", "5 ml", "30 ml", "80 und", "150 g", "200 ml", "300 g", "150 ml", "2 L", "1 unidad"],
        'Etapa': ["Adulto", "Adulto", "Adulto", "Bebé", "Adulto", "Adulto", "Adulto", "Adulto", "Adulto", "Bebé", "Adulto", "Adulto", "Adulto", "Bebé", "Adulto", "Adulto"],
        'Tipo de piel': ["Todo tipo de piel", "Piel sensible", "No aplica", "Piel del bebé", "No aplica", "No aplica", "No aplica", "Todo tipo de piel", "Piel con manchas", "Piel del bebé", "No aplica", "Piel sensible", "No aplica", "Piel del bebé", "No aplica", "No aplica"],
        'Tipo de cabello': ["No aplica", "No aplica", "Cabello dañado", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica", "No aplica"]
    }
    dummy_df = pd.DataFrame(dummy_data)
    input_test_file = "dummy_input_catalog.csv"
    dummy_df.to_csv(input_test_file, index=False, encoding='utf-8-sig')
    print(f"Dummy input file '{input_test_file}' created for testing.")

    # Process the dummy file
    enrich_product_catalog(input_test_file, "enriched_dummy_catalog_output.csv")

    # To run with your actual file:
    enrich_product_catalog("C:/Users/PC/Documents/Farmatodo/enriched_Maestro_v2.csv", "C:/Users/PC/Documents/Farmatodo/Enriched_master_final.csv")