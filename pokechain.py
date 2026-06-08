import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests


# ==========================================
# LÓGICA DE DETECCIÓN DE POKÉMON
# ==========================================
def analizar_nombre(nombre_sucio):
    es_shadow = re.search(r"\(Shadow\)", nombre_sucio, re.IGNORECASE) or \
                re.search(r"\(Oscuro\)", nombre_sucio, re.IGNORECASE)

    if es_shadow:
        prefijo = "Shadow&" if idioma.get() == "English" else "Oscuro&"
    else:
        prefijo = ""

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


def criterio_ordenacion(elemento):
    """
    Extrae el ID numérico de la cadena (ej. 'Shadow&+150' -> 150)
    para poder ordenar la lista numéricamente de menor a mayor.
    """
    match = re.search(r"\+(\d+)", elemento)
    if match:
        return int(match.group(1))
    return 0


# ==========================================
# ACCIONES DE LA INTERFAZ
# ==========================================
def procesar_lista():
    btn_procesar.config(state=tk.DISABLED, text="Procesando...")
    ventana.update_idletasks()

    texto_entrada = txt_entrada.get("1.0", tk.END)
    lineas = [
        linea.strip()
        for linea in texto_entrada.split("\n")
        if linea.strip()
    ]

    if not lineas:
        messagebox.showwarning(
            "Aviso", "Por favor, introduce al menos un Pokémon."
        )
        btn_procesar.config(state=tk.NORMAL, text="Convertir Lista")
        return

    # Usamos un conjunto para evitar duplicados
    ids_unicos = set()

    for poke in lineas:
        resultado_poke = obtener_anteevolucion_id(poke)
        if resultado_poke:
            ids_unicos.add(resultado_poke)

    # Convertimos a lista y ordenamos usando nuestra regla numérica personalizada
    lista_ordenada = sorted(list(ids_unicos), key=criterio_ordenacion)

    # Unimos todo con puntos y comas
    resultado_final = ";".join(lista_ordenada)

    if resultado_final:
        resultado_final += ";"

    txt_salida.config(state=tk.NORMAL)
    txt_salida.delete("1.0", tk.END)
    txt_salida.insert(tk.END, resultado_final)
    txt_salida.config(state=tk.DISABLED)

    lbl_aviso.config(text="")
    btn_procesar.config(state=tk.NORMAL, text="Convertir Lista")


def copiar_al_portapapeles():
    contenido = txt_salida.get("1.0", tk.END).strip()
    if contenido:
        ventana.clipboard_clear()
        ventana.clipboard_append(contenido)
        messagebox.showinfo(
            "Copiado", "¡Cadena copiada al portapapeles con éxito!"
        )
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
    aplicar_liga("PC-1500&3-4puntos de salud&3-4defensa&0-1ataque&!#&")


def aplicar_ultra_league():
    aplicar_liga(
        "PC-2500&3-4puntos de salud&3-4defensa&0-1ataque&!#&",
        aviso="⚠ Advertencia: algunos Pokémon de la UltraLeague requieren IVs 100% como el caso de Cradily. Para Pokémon de estas características, revisar a mano.",
    )


# ==========================================
# DISEÑO DE LA VENTANA (GUI)
# ==========================================
ventana = tk.Tk()
ventana.title("PokeChain")
ventana.geometry("500x700")
ventana.configure(bg="#f0f0f0")
img = tk.PhotoImage(file="icono.png")
ventana.iconphoto(True, img)

# Frame para la etiqueta de entrada y el desplegable de idioma en la misma fila
frame_entrada_header = tk.Frame(ventana, bg="#f0f0f0")
frame_entrada_header.pack(anchor="w", padx=20, pady=(15, 5), fill=tk.X)

lbl_entrada = tk.Label(
    frame_entrada_header,
    text="1. Pega aquí tu lista de Pokémon:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_entrada.pack(side=tk.LEFT)

idioma = tk.StringVar(value="Español")
menu_idioma = tk.OptionMenu(frame_entrada_header, idioma, "Español", "English")
menu_idioma.config(font=("Arial", 9), bg="#f0f0f0")
menu_idioma.pack(side=tk.RIGHT)

txt_entrada = scrolledtext.ScrolledText(
    ventana, height=10, width=55, wrap=tk.WORD
)
txt_entrada.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

btn_procesar = tk.Button(
    ventana,
    text="Convertir Lista",
    command=procesar_lista,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=5,
)
btn_procesar.pack(pady=15)

lbl_salida = tk.Label(
    ventana,
    text="2. Resultado ordenado por ID (Sin repetidos):",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_salida.pack(anchor="w", padx=20, pady=(10, 5))

txt_salida = scrolledtext.ScrolledText(
    ventana, height=10, width=55, wrap=tk.CHAR, state=tk.DISABLED
)
txt_salida.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

# Frame para los dos botones de liga en la misma fila
frame_ligas = tk.Frame(ventana, bg="#f0f0f0")
frame_ligas.pack(pady=(5, 0))

btn_great = tk.Button(
    frame_ligas,
    text="Great League",
    command=aplicar_great_league,
    bg="#7B68EE",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=5,
)
btn_great.pack(side=tk.LEFT, padx=10)

btn_ultra = tk.Button(
    frame_ligas,
    text="Ultra League",
    command=aplicar_ultra_league,
    bg="#FF8C00",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=5,
)
btn_ultra.pack(side=tk.LEFT, padx=10)

lbl_aviso = tk.Label(
    ventana,
    text="",
    bg="#f0f0f0",
    fg="#B8860B",
    font=("Arial", 9),
    wraplength=460,
    justify="left",
    height=3,
)
lbl_aviso.pack(anchor="w", padx=20, pady=(5, 0))

btn_copiar = tk.Button(
    ventana,
    text="Copiar al Portapapeles",
    command=copiar_al_portapapeles,
    bg="#008CBA",
    fg="white",
    font=("Arial", 10, "bold"),
    padx=10,
    pady=5,
)
btn_copiar.pack(pady=15)

ventana.mainloop()