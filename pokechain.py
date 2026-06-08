import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests


# ==========================================
# LÓGICA DE DETECCIÓN DE POKÉMON
# ==========================================
def limpiar_nombre(nombre_sucio):
    nombre_limpio = re.sub(r"\s*\(.*\)", "", nombre_sucio)
    return nombre_limpio.strip().lower()


def obtener_anteevolucion_id(nombre_pokemon):
    nombre = limpiar_nombre(nombre_pokemon)
    if not nombre:
        return None

    url_especie = f"https://pokeapi.co/api/v2/pokemon-species/{nombre}/"

    try:
        respuesta = requests.get(url_especie)
        if respuesta.status_code != 200:
            return None

        datos_especie = respuesta.json()

        # Obtiene la anteevolución directa si existe, si no, su propio ID
        if datos_especie.get("evolves_from_species"):
            url_anteevolucion = datos_especie["evolves_from_species"]["url"]
            id_anteevolucion = url_anteevolucion.split("/")[-2]
            return id_anteevolucion
        else:
            return datos_especie["id"]

    except Exception:
        return None


# ==========================================
# ACCIONES DE LA INTERFAZ
# ==========================================
def procesar_lista():
    # Deshabilitamos el botón temporalmente para que no hagan doble clic
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
        poke_id = obtener_anteevolucion_id(poke)
        if poke_id:
            ids_formateados.append(f"+{poke_id}")

    resultado_final = ";".join(ids_formateados)

    # Insertar el resultado en el cuadro de salida
    txt_salida.config(state=tk.NORMAL)  # Habilitamos temporalmente para escribir
    txt_salida.delete("1.0", tk.END)
    txt_salida.insert(tk.END, resultado_final)
    txt_salida.config(state=tk.DISABLED)  # Lo volvemos a dejar de solo lectura

    # Restaurar botón
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

# Etiqueta Entrada
lbl_entrada = tk.Label(
    ventana,
    text="1. Pega aquí tu lista de Pokémon:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_entrada.pack(anchor="w", padx=20, pady=(15, 5))

# Caja de texto de Entrada
txt_entrada = scrolledtext.ScrolledText(
    ventana, height=10, width=55, wrap=tk.WORD
)
txt_entrada.pack(padx=20, pady=5)

# Botón Procesar
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

# Etiqueta Salida
lbl_salida = tk.Label(
    ventana,
    text="2. Resultado en formato de cadena:",
    bg="#f0f0f0",
    font=("Arial", 10, "bold"),
)
lbl_salida.pack(anchor="w", padx=20, pady=(10, 5))

# Caja de texto de Salida (Bloqueada para que no se edite sin querer)
txt_salida = scrolledtext.ScrolledText(
    ventana, height=5, width=55, wrap=tk.CHAR, state=tk.DISABLED
)
txt_salida.pack(padx=20, pady=5)

# Botón Copiar
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

# Ejecutar la aplicación
ventana.mainloop()