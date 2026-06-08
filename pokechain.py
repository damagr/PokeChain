import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests


# ==========================================
# LÓGICA DE DETECCIÓN DE POKÉMON
# ==========================================
def analizar_nombre(nombre_sucio):
    # Detectamos si contiene (Shadow) u (Oscuro) antes de limpiar el nombre
    prefijo = ""
    if re.search(r"\(Shadow\)", nombre_sucio, re.IGNORECASE):
        prefijo = "Shadow&"
    elif re.search(r"\(Oscuro\)", nombre_sucio, re.IGNORECASE):
        prefijo = "Oscuro&"

    # Limpiamos el nombre eliminando cualquier paréntesis para la API
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

        # Bucle para subir hasta la raíz de la cadena evolutiva
        while datos_especie.get("evolves_from_species"):
            url_anteevolucion = datos_especie["evolves_from_species"]["url"]

            respuesta = requests.get(url_anteevolucion)
            if respuesta.status_code == 200:
                datos_especie = respuesta.json()
            else:
                break

        # Devolvemos el prefijo ("Shadow&", "Oscuro&" o "") junto al +ID
        return f"{prefijo}+{datos_especie['id']}"

    except Exception:
        return None


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

    ids_formateados = []

    for poke in lineas:
        resultado_poke = obtener_anteevolucion_id(poke)
        if resultado_poke:
            ids_formateados.append(resultado_poke)

    # Unimos todo con puntos y comas
    resultado_final = ";".join(ids_formateados)

    # Si hay resultados, añadimos un punto y coma al final de toda la cadena si lo necesitas
    if resultado_final:
        resultado_final += ";"

    txt_salida.config(state=tk.NORMAL)
    txt_salida.delete("1.0", tk.END)
    txt_salida.insert(tk.END, resultado_final)
    txt_salida.config(state=tk.DISABLED)

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


# ==========================================
# DISEÑO DE LA VENTANA (GUI)
# ==========================================
ventana = tk.Tk()
ventana.title("Buscador de Anteevoluciones")
ventana.geometry("500x600")
ventana.configure(bg="#f0f0f0")

lbl_entrada = tk.Label(
    ventana,
    text="1. Pega aquí tu lista de Pokémon:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_entrada.pack(anchor="w", padx=20, pady=(15, 5))

txt_entrada = scrolledtext.ScrolledText(
    ventana, height=10, width=55, wrap=tk.WORD
)
txt_entrada.pack(padx=20, pady=5)

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
    text="2. Resultado en formato de cadena:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_salida.pack(anchor="w", padx=20, pady=(10, 5))

txt_salida = scrolledtext.ScrolledText(
    ventana, height=5, width=55, wrap=tk.CHAR, state=tk.DISABLED
)
txt_salida.pack(padx=20, pady=5)

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