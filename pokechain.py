import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import os
import requests


# ==========================================
# LÓGICA COMPARTIDA
# ==========================================
def get_prefijo_shadow():
    return "Shadow&" if idioma.get() == "English" else "Oscuro&"


def criterio_ordenacion(elemento):
    # Busca el primer número secuencial que aparezca en el elemento, 
    # sin importar los caracteres o palabras que tenga delante (!, Fuego&, Oscuro&, etc.)
    match = re.search(r"\d+", elemento)
    if match:
        return int(match.group(0))
    return 0


# ==========================================
# PESTAÑA 1 — LÓGICA
# ==========================================
def analizar_nombre(nombre_sucio):
    es_shadow = re.search(r"\(Shadow\)", nombre_sucio, re.IGNORECASE) or \
                re.search(r"\(Oscuro\)", nombre_sucio, re.IGNORECASE)
    prefijo = get_prefijo_shadow() if es_shadow else ""
    nombre_limpio = re.sub(r"\s*\(.*\)", "", nombre_sucio)
    return nombre_limpio.strip().lower(), prefijo


def obtener_anteevolucion_id(nombre_pokemon):
    nombre, prefijo = analizar_nombre(nombre_pokemon)
    if not nombre:
        return None
    try:
        url_especie = f"https://pokeapi.co/api/v2/pokemon-species/{nombre}/"
        respuesta = requests.get(url_especie)
        if respuesta.status_code != 200:
            return None
        datos_especie = respuesta.json()
        while datos_especie.get("evolves_from_species"):
            url_anteevolucion = datos_especie["evolves_from_species"]["url"]
            respuesta = requests.get(url_anteevolucion)
            if respuesta.status_code == 200:
                datos_especie = respuesta.json()
            else:
                break
        return f"{prefijo}+{datos_especie['id']}"
    except Exception:
        return None


def procesar_lista():
    btn_procesar.config(state=tk.DISABLED, text="Procesando...")
    ventana.update_idletasks()

    texto_entrada = txt_entrada.get("1.0", tk.END)
    lineas = [l.strip() for l in texto_entrada.split("\n") if l.strip()]

    if not lineas:
        messagebox.showwarning("Aviso", "Por favor, introduce al menos un Pokémon.")
        btn_procesar.config(state=tk.NORMAL, text="Convertir Lista")
        return

    ids_unicos = set()
    for poke in lineas:
        resultado = obtener_anteevolucion_id(poke)
        if resultado:
            ids_unicos.add(resultado)

    lista_ordenada = sorted(list(ids_unicos), key=criterio_ordenacion)
    resultado_final = ";".join(lista_ordenada)
    if resultado_final:
        resultado_final += ";"

    txt_salida.config(state=tk.NORMAL)
    txt_salida.delete("1.0", tk.END)
    txt_salida.insert(tk.END, resultado_final)
    txt_salida.config(state=tk.DISABLED)

    lbl_aviso.config(text="")
    btn_procesar.config(state=tk.NORMAL, text="Convertir Lista")


def copiar_tab1():
    contenido = txt_salida.get("1.0", tk.END).strip()
    if contenido:
        ventana.clipboard_clear()
        ventana.clipboard_append(contenido)
        messagebox.showinfo("Copiado", "¡Cadena copiada al portapapeles con éxito!")
    else:
        messagebox.showwarning("Aviso", "No hay nada que copiar todavía.")


def aplicar_liga(prefijo_liga, aviso=""):
    contenido = txt_salida.get("1.0", tk.END).strip()
    if not contenido:
        messagebox.showwarning("Aviso", "No hay resultado al que añadir la liga.")
        return
    txt_salida.config(state=tk.NORMAL)
    txt_salida.delete("1.0", tk.END)
    txt_salida.insert(tk.END, prefijo_liga + contenido)
    txt_salida.config(state=tk.DISABLED)
    lbl_aviso.config(text=aviso)


def aplicar_great_league():
    aplicar_liga("PC-1500&3-4puntos de salud&3-4defensa&0-1ataque&")


def aplicar_ultra_league():
    aplicar_liga(
        "PC-2500&3-4puntos de salud&3-4defensa&0-1ataque&",
        ##aviso="⚠ Advertencia: algunos Pokémon de la UltraLeague requieren IVs 100% como el caso de Cradily. Para Pokémon de estas características, revisar a mano.",
    )


def limpiar_tab1():
    txt_entrada.delete("1.0", tk.END)
    txt_salida.config(state=tk.NORMAL)
    txt_salida.delete("1.0", tk.END)
    txt_salida.config(state=tk.DISABLED)
    lbl_aviso.config(text="")


# ==========================================
# PESTAÑA 2 — LÓGICA
# ==========================================
def parsear_cadena_existente(cadena):
    """
    Parsea una cadena compleja manteniendo filtros personalizados.
    - Elimina específicamente los modificadores Mega (ej: Mega1-).
    - Elimina por completo elementos que contengan la palabra 'investigación'.
    - Traduce automáticamente los tipos de Español a Inglés si está seleccionado "English".
    - Preserva intactos filtros de tipos, exclusiones (!Hielo, !146), etc.
    """
    resultados = set()
    # Separar la cadena por comas y puntos y comas
    tokens = re.split(r"[,;]", cadena)

    # Diccionario de mapeo basado en las imágenes (Español -> Inglés)
    # Incluye expresiones regulares para curarnos en salud con las tildes
    traduccion_tipos = {
        r'normal': 'Normal',
        r'fuego': 'Fire',
        r'agua': 'Water',
        r'planta': 'Grass',
        r'el[eé]ctrico': 'Electric',
        r'hielo': 'Ice',
        r'lucha': 'Fighting',
        r'veneno': 'Poison',
        r'tierra': 'Ground',
        r'volador': 'Flying',
        r'ps[ií]quico': 'Psychic',
        r'bicho': 'Bug',
        r'roca': 'Rock',
        r'fantasma': 'Ghost',
        r'drag[oó]n': 'Dragon',
        r'siniestro': 'Dark',
        r'acero': 'Steel',
        r'hada': 'Fairy'
    }

    for token in tokens:
        token = token.strip()
        if not token:
            continue

        # Si el elemento contiene la palabra investigación, se descarta por completo
        if re.search(r'investigaci[oó]n', token, flags=re.IGNORECASE):
            continue

        # Eliminamos el modificador Mega/Mega1- junto con el '&' que lo une
        token_limpio = re.sub(r'\bmega\d*-?&|&\bmega\d*-?|\bmega\d*-?', '', token, flags=re.IGNORECASE)
        token_limpio = token_limpio.strip('& ')

        if not token_limpio:
            continue

        # TRADUCCIÓN DINÁMICA: Si está en inglés, cambiamos los tipos de idioma
        if idioma.get() == "English":
            for esp_patron, ing_valor in traduccion_tipos.items():
                # \b asegura que cambie la palabra exacta (ej: 'Fuego' -> 'Fire') sin romper otras cosas
                token_limpio = re.sub(rf'\b{esp_patron}\b', ing_valor, token_limpio, flags=re.IGNORECASE)

        # Si el resultado es un ID numérico puro (ej: 806), añadimos '+' para el estándar de la app
        if re.match(r"^\d+$", token_limpio):
            token_limpio = f"+{token_limpio}"
        else:
            # Si es un formato "Oscuro&643" o "Shadow&643", lo estandarizamos usando get_prefijo_shadow()
            if re.match(r'^(oscuro&|shadow&)\d+$', token_limpio, flags=re.IGNORECASE):
                num = re.search(r'\d+', token_limpio).group()
                token_limpio = f"{get_prefijo_shadow()}+{num}"

        resultados.add(token_limpio)

    return resultados


def procesar_concatenar():
    btn_concat.config(state=tk.DISABLED, text="Procesando...")
    ventana.update_idletasks()

    cadena_existente = txt_cadena_entrada.get("1.0", tk.END).strip()
    if not cadena_existente:
        messagebox.showwarning("Aviso", "Por favor, introduce una cadena.")
        btn_concat.config(state=tk.NORMAL, text="Limpiar y ordenar")
        return

    ids = parsear_cadena_existente(cadena_existente)

    if not ids:
        messagebox.showwarning("Aviso", "No se encontraron IDs válidos en la cadena.")
        btn_concat.config(state=tk.NORMAL, text="Limpiar y ordenar")
        return

    lista_ordenada = sorted(list(ids), key=criterio_ordenacion)
    cadena_limpia = ";".join(lista_ordenada) + ";"
    resultado_final = "4*;3*;3-ataque&!#&" + cadena_limpia

    txt_cadena_salida.config(state=tk.NORMAL)
    txt_cadena_salida.delete("1.0", tk.END)
    txt_cadena_salida.insert(tk.END, resultado_final)
    txt_cadena_salida.config(state=tk.DISABLED)

    btn_concat.config(state=tk.NORMAL, text="Limpiar y ordenar")


def copiar_tab2():
    contenido = txt_cadena_salida.get("1.0", tk.END).strip()
    if contenido:
        ventana.clipboard_clear()
        ventana.clipboard_append(contenido)
        messagebox.showinfo("Copiado", "¡Cadena copiada al portapapeles con éxito!")
    else:
        messagebox.showwarning("Aviso", "No hay nada que copiar todavía.")


def limpiar_tab2():
    txt_cadena_entrada.delete("1.0", tk.END)
    txt_cadena_salida.config(state=tk.NORMAL)
    txt_cadena_salida.delete("1.0", tk.END)
    txt_cadena_salida.config(state=tk.DISABLED)


# ==========================================
# VENTANA PRINCIPAL
# ==========================================
ventana = tk.Tk()
ventana.title("PokeChain")
ventana.geometry("500x750")
ventana.configure(bg="#f0f0f0")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_icono = os.path.join(BASE_DIR, "icono.png")
if os.path.exists(_icono):
    img = tk.PhotoImage(file=_icono)
    ventana.iconphoto(True, img)

# Idioma global (compartido entre pestañas)
idioma = tk.StringVar(value="Español")

# ==========================================
# NOTEBOOK (pestañas)
# ==========================================
notebook = ttk.Notebook(ventana)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ==========================================
# PESTAÑA 1 — BUSCADOR DE ANTEEVOLUCIONES
# ==========================================
tab1 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab1, text="PVP")

frame_entrada_header = tk.Frame(tab1, bg="#f0f0f0")
frame_entrada_header.pack(anchor="w", padx=20, pady=(15, 5), fill=tk.X)

lbl_entrada = tk.Label(
    frame_entrada_header,
    text="1. Pega aquí tu lista de Pokémon:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_entrada.pack(side=tk.LEFT)

menu_idioma = tk.OptionMenu(frame_entrada_header, idioma, "Español", "English")
menu_idioma.config(font=("Arial", 9), bg="#f0f0f0")
menu_idioma.pack(side=tk.RIGHT)

txt_entrada = scrolledtext.ScrolledText(tab1, height=10, width=55, wrap=tk.WORD)
txt_entrada.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

frame_acciones = tk.Frame(tab1, bg="#f0f0f0")
frame_acciones.pack(pady=15)

btn_procesar = tk.Button(
    frame_acciones, text="Convertir Lista", command=procesar_lista,
    bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_procesar.pack(side=tk.LEFT, padx=10)

btn_limpiar = tk.Button(
    frame_acciones, text="Limpiar", command=limpiar_tab1,
    bg="#e0e0e0", fg="#333333", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_limpiar.pack(side=tk.LEFT, padx=10)

lbl_salida = tk.Label(
    tab1, text="2. Resultado ordenado por ID (Sin repetidos):",
    bg="#f0f0f0", font=("Arial", 10, "bold"),
)
lbl_salida.pack(anchor="w", padx=20, pady=(10, 5))

txt_salida = scrolledtext.ScrolledText(tab1, height=10, width=55, wrap=tk.CHAR, state=tk.DISABLED)
txt_salida.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

frame_ligas = tk.Frame(tab1, bg="#f0f0f0")
frame_ligas.pack(pady=(5, 0))

btn_great = tk.Button(
    frame_ligas, text="Great League", command=aplicar_great_league,
    bg="#7B68EE", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_great.pack(side=tk.LEFT, padx=10)

btn_ultra = tk.Button(
    frame_ligas, text="Ultra League", command=aplicar_ultra_league,
    bg="#FF8C00", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_ultra.pack(side=tk.LEFT, padx=10)

lbl_aviso = tk.Label(
    tab1, text="", bg="#f0f0f0", fg="#B8860B", font=("Arial", 9),
    wraplength=460, justify="left", height=3,
)
lbl_aviso.pack(anchor="w", padx=20, pady=(5, 0))

btn_copiar = tk.Button(
    tab1, text="Copiar al Portapapeles", command=copiar_tab1,
    bg="#008CBA", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_copiar.pack(pady=15)

# ==========================================
# PESTAÑA 2 — LIMPIADOR DE CADENA
# ==========================================
tab2 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab2, text="Dialgadex helper")

# Contenedor para alinear la etiqueta y el selector de idioma a la derecha
frame_entrada_header2 = tk.Frame(tab2, bg="#f0f0f0")
frame_entrada_header2.pack(anchor="w", padx=20, pady=(15, 5), fill=tk.X)

lbl_cadena_entrada = tk.Label(
    frame_entrada_header2,
    text="1. Pega aquí la cadena existente:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_cadena_entrada.pack(side=tk.LEFT)

# Replicamos el selector apuntando a la misma variable global 'idioma'
menu_idioma2 = tk.OptionMenu(frame_entrada_header2, idioma, "Español", "English")
menu_idioma2.config(font=("Arial", 9), bg="#f0f0f0")
menu_idioma2.pack(side=tk.RIGHT)

# Mantenemos la altura corregida (height=6) para que no se corte el diseño
txt_cadena_entrada = scrolledtext.ScrolledText(tab2, height=6, width=55, wrap=tk.WORD)
txt_cadena_entrada.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

frame_acciones2 = tk.Frame(tab2, bg="#f0f0f0")
frame_acciones2.pack(pady=15)

btn_concat = tk.Button(
    frame_acciones2, text="Limpiar y ordenar", command=procesar_concatenar,
    bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_concat.pack(side=tk.LEFT, padx=10)

btn_limpiar2 = tk.Button(
    frame_acciones2, text="Limpiar", command=limpiar_tab2,
    bg="#e0e0e0", fg="#333333", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_limpiar2.pack(side=tk.LEFT, padx=10)

lbl_cadena_salida = tk.Label(
    tab2, text="2. Cadena resultante:",
    bg="#f0f0f0", font=("Arial", 10, "bold"),
)
lbl_cadena_salida.pack(anchor="w", padx=20, pady=(10, 5))

txt_cadena_salida = scrolledtext.ScrolledText(tab2, height=10, width=55, wrap=tk.CHAR, state=tk.DISABLED)
txt_cadena_salida.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

btn_copiar2 = tk.Button(
    tab2, text="Copiar al Portapapeles", command=copiar_tab2,
    bg="#008CBA", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_copiar2.pack(pady=15)

ventana.mainloop()