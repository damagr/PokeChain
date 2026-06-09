import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import os
import requests

_CACHE_ESPECIE = {}
_CACHE_DIALGADEX = None
_CACHE_IDS_TAB1 = None
_CACHE_IDS_TAB2 = None
_SESSION = requests.Session()
_TIMEOUT = 15

DIALGADEX_URL = "https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_pkm.min.json"


# ==========================================
# TOOLTIP
# ==========================================
class Tooltip:
    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.tip = None
        widget.bind("<Enter>", self._mostrar)
        widget.bind("<Leave>", self._ocultar)

    def _mostrar(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tip, text=self.texto, background="#333333", foreground="white",
            font=("Segoe UI", 9), padx=8, pady=4, relief="flat",
        )
        label.pack()

    def _ocultar(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ==========================================
# TEXTINPUT — Widget de texto robusto
# ==========================================
class TextInput(tk.Frame):
    def __init__(self, master, height=8, font=None, wrap=tk.WORD, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text = tk.Text(
            self, height=height, font=font or ("Consolas", 10),
            wrap=wrap, undo=False, yscrollcommand=self.scrollbar.set,
            borderwidth=0, highlightthickness=0, padx=6, pady=6,
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text.yview)

    def get_text(self, start="1.0", end=tk.END):
        return self.text.get(start, end)

    def set_text(self, contenido):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, contenido)
        self.text.see("1.0")

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

    def set_state(self, state):
        self.text.config(state=state)

    def paste_clipboard(self, label_contador=None):
        try:
            texto = self.text.clipboard_get()
        except tk.TclError:
            return
        if not texto:
            return
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, texto)
        self.text.see("1.0")
        if label_contador:
            self._actualizar_contador(label_contador)

    def _actualizar_contador(self, label):
        contenido = self.text.get("1.0", tk.END).strip()
        if not contenido:
            label.config(text="")
            return
        lineas = contenido.count("\n") + 1
        chars = len(contenido)
        label.config(text=f"{lineas} lineas - {chars} caracteres")


# ==========================================
# LÓGICA COMPARTIDA
# ==========================================
def get_prefijo_shadow():
    return "Shadow&" if idioma.get() == "English" else "Oscuro&"


def criterio_ordenacion(elemento):
    match = re.search(r"\d+", elemento)
    if match:
        return int(match.group(0))
    return 0


def _consulta_api(url):
    clave = url.lower()
    if clave in _CACHE_ESPECIE:
        return _CACHE_ESPECIE[clave]
    try:
        r = _SESSION.get(url, timeout=_TIMEOUT)
        if r.status_code == 200:
            _CACHE_ESPECIE[clave] = r.json()
            return _CACHE_ESPECIE[clave]
    except Exception:
        pass
    return None


def _limpiar_nombre_especie(nombre):
    nombre = re.sub(r"^(Mega|Shadow)\s+", "", nombre)
    nombre = re.sub(r"\s+[XYZ]$", "", nombre)
    return nombre.strip()


def buscar_anteevolucion_por_nombre(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{nombre.lower().strip()}/"
    datos = _consulta_api(url)
    if not datos:
        return None
    while datos.get("evolves_from_species"):
        padre = _consulta_api(datos["evolves_from_species"]["url"])
        if not padre:
            break
        datos = padre
    return str(datos["id"])


def pegar_completo(event, text_input, label_contador=None):
    text_input.paste_clipboard(label_contador)
    return "break"


# ==========================================
# PESTAÑA 1 — LÓGICA
# ==========================================
def analizar_nombre(nombre_sucio):
    es_shadow = re.search(r"\(Shadow\)", nombre_sucio, re.IGNORECASE) or \
                re.search(r"\(Oscuro\)", nombre_sucio, re.IGNORECASE)
    prefijo = get_prefijo_shadow() if es_shadow else ""
    nombre_limpio = re.sub(r"\s*\(.*?\)", "", nombre_sucio)
    return nombre_limpio.strip().lower(), prefijo


def _analizar_raw(nombre_sucio):
    es_shadow = bool(re.search(r"\(Shadow\)|\(Oscuro\)", nombre_sucio, re.IGNORECASE))
    nombre_limpio = re.sub(r"\s*\(.*?\)", "", nombre_sucio).strip().lower()
    return nombre_limpio, es_shadow


def obtener_anteevolucion_id(nombre_pokemon):
    nombre, prefijo = analizar_nombre(nombre_pokemon)
    if not nombre:
        return None
    datos_especie = _consulta_api(
        f"https://pokeapi.co/api/v2/pokemon-species/{nombre}/"
    )
    if not datos_especie:
        return None
    while datos_especie.get("evolves_from_species"):
        padre = _consulta_api(datos_especie["evolves_from_species"]["url"])
        if not padre:
            break
        datos_especie = padre
    return f"{prefijo}+{datos_especie['id']}"


def _obtener_id_raw(nombre_pokemon):
    nombre, es_shadow = _analizar_raw(nombre_pokemon)
    if not nombre:
        return None
    datos_especie = _consulta_api(
        f"https://pokeapi.co/api/v2/pokemon-species/{nombre}/"
    )
    if not datos_especie:
        return None
    while datos_especie.get("evolves_from_species"):
        padre = _consulta_api(datos_especie["evolves_from_species"]["url"])
        if not padre:
            break
        datos_especie = padre
    return (datos_especie["id"], es_shadow)


def _regenerar_tab1():
    if _CACHE_IDS_TAB1 is None:
        return
    prefijo_shadow = get_prefijo_shadow()
    items = []
    for id_num, es_shadow in _CACHE_IDS_TAB1:
        pref = prefijo_shadow if es_shadow else ""
        items.append(f"{pref}+{id_num}")
    lista_ordenada = sorted(items, key=criterio_ordenacion)
    resultado = ";".join(lista_ordenada)
    if resultado:
        resultado += "&!#"
    output_pokemon.set_text(resultado)
    output_pokemon.set_state(tk.DISABLED)


def _regenerar_tab2():
    if _CACHE_IDS_TAB2 is None:
        return
    prefijo_shadow = get_prefijo_shadow()
    prefijo_calidad = "4*,3*&3-attack&" if idioma.get() == "English" else "4*;3*&3-ataque&"
    items = []
    for id_base, es_shadow in _CACHE_IDS_TAB2:
        pref = prefijo_shadow if es_shadow else ""
        items.append(f"{pref}+{id_base}")
    lista_ordenada = sorted(items, key=criterio_ordenacion)
    resultado = prefijo_calidad + ";".join(lista_ordenada) + "&!#"
    output_atacantes.set_text(resultado)
    output_atacantes.set_state(tk.DISABLED)


def procesar_lista():
    global _CACHE_IDS_TAB1
    btn_procesar.config(state=tk.DISABLED, text="Procesando...")
    frame_progreso1.pack(padx=20, pady=5, fill=tk.X)
    progress_bar1["value"] = 0
    ventana.update_idletasks()

    texto_entrada = input_pokemon.get_text()
    lineas = [l.strip() for l in texto_entrada.split("\n") if l.strip()]

    if not lineas:
        messagebox.showwarning("Aviso", "Por favor, introduce al menos un Pokemon.")
        btn_procesar.config(state=tk.NORMAL, text="Convertir Lista")
        frame_progreso1.pack_forget()
        return

    total = len(lineas)
    progress_bar1["maximum"] = total
    _CACHE_IDS_TAB1 = set()
    for i, poke in enumerate(lineas):
        resultado = _obtener_id_raw(poke)
        if resultado:
            _CACHE_IDS_TAB1.add(resultado)
        progress_bar1["value"] = i + 1
        lbl_progreso1.config(text=f"{i+1}/{total} ({100*(i+1)//total}%)")
        ventana.update_idletasks()

    _regenerar_tab1()

    btn_procesar.config(state=tk.NORMAL, text="Convertir Lista")
    frame_progreso1.pack_forget()


def copiar_tab1():
    contenido = output_pokemon.get_text().strip()
    if contenido:
        ventana.clipboard_clear()
        ventana.clipboard_append(contenido)
        messagebox.showinfo("Copiado", "Cadena copiada al portapapeles con exito!")
    else:
        messagebox.showwarning("Aviso", "No hay nada que copiar todavia.")


_PREFIJOS_LIGA = [
    "cp-1500&-1attack&3-defense&3-hp&",
    "cp-2500&-1attack&3-defense&3-hp&",
    "PC-1500&3-4puntos de salud&3-4defensa&0-1ataque&",
    "PC-2500&3-4puntos de salud&3-4defensa&0-1ataque&",
]

def aplicar_liga(prefijo_liga, aviso=""):
    contenido = output_pokemon.get_text().strip()
    if not contenido:
        messagebox.showwarning("Aviso", "No hay resultado al que anadir la liga.")
        return
    for p in _PREFIJOS_LIGA:
        if contenido.startswith(p):
            contenido = contenido[len(p):]
            break
    output_pokemon.set_text(prefijo_liga + contenido)
    output_pokemon.set_state(tk.DISABLED)


def aplicar_great_league():
    if idioma.get() == "English":
        aplicar_liga("cp-1500&-1attack&3-defense&3-hp&")
    else:
        aplicar_liga("PC-1500&3-4puntos de salud&3-4defensa&0-1ataque&")


def aplicar_ultra_league():
    if idioma.get() == "English":
        aplicar_liga("cp-2500&-1attack&3-defense&3-hp&")
    else:
        aplicar_liga("PC-2500&3-4puntos de salud&3-4defensa&0-1ataque&")


def limpiar_tab1():
    input_pokemon.clear()
    output_pokemon.set_text("")
    output_pokemon.set_state(tk.DISABLED)


# ==========================================
# PESTAÑA 2 — LOGICA: MEJORES ATACANTES
# ==========================================
def descargar_datos_dialgadex():
    global _CACHE_DIALGADEX
    if _CACHE_DIALGADEX is not None:
        return _CACHE_DIALGADEX
    try:
        r = _SESSION.get(DIALGADEX_URL, timeout=30)
        if r.status_code == 200:
            _CACHE_DIALGADEX = r.json()
            return _CACHE_DIALGADEX
    except Exception:
        pass
    return None


def filtrar_atacantes(datos, inedito, mega, oscuro, legendario):
    resultado = []
    for p in datos:
        incluir = False
        es_normal = (p.get("class") is None
                     and not p.get("shadow", False)
                     and p.get("form", "Normal") == "Normal"
                     and p.get("released", False))
        if es_normal:
            incluir = True
        if oscuro and p.get("shadow", False):
            incluir = True
        if legendario and p.get("class") in (
            "POKEMON_CLASS_LEGENDARY",
            "POKEMON_CLASS_MYTHIC",
            "POKEMON_CLASS_ULTRA_BEAST",
        ):
            incluir = True
        if mega and p.get("form") in ("Mega", "MegaY", "MegaZ"):
            incluir = True
        if inedito and not p.get("released", True):
            incluir = True
        if incluir:
            resultado.append(p)
    resultado.sort(key=lambda x: x.get("stats", {}).get("baseAttack", 0), reverse=True)
    return resultado


def generar_cadena_atacantes(lista_pokemon, cantidad):
    global _CACHE_IDS_TAB2
    btn_obtener_atacantes.config(state=tk.DISABLED, text="Procesando...")
    frame_progreso2.pack(padx=20, pady=5, fill=tk.X)
    progress_bar2["value"] = 0
    ventana.update_idletasks()

    top = lista_pokemon[:cantidad]

    total = len(top)
    progress_bar2["maximum"] = total
    _CACHE_IDS_TAB2 = set()
    for i, p in enumerate(top):
        nombre = _limpiar_nombre_especie(p["name"])
        es_shadow = p.get("shadow", False)

        id_base = buscar_anteevolucion_por_nombre(nombre)
        if not id_base:
            id_base = p["id"]

        _CACHE_IDS_TAB2.add((int(id_base), es_shadow))

        progress_bar2["value"] = i + 1
        lbl_progreso2.config(text=f"{i+1}/{total} ({100*(i+1)//total}%)")
        ventana.update_idletasks()

    _regenerar_tab2()

    btn_obtener_atacantes.config(state=tk.NORMAL, text="Obtener Lista")
    frame_progreso2.pack_forget()


def obtener_lista_atacantes():
    btn_obtener_atacantes.config(state=tk.DISABLED, text="Descargando...")
    ventana.update_idletasks()

    datos = descargar_datos_dialgadex()
    if not datos:
        messagebox.showerror("Error", "No se pudieron descargar los datos de DialgaDex.")
        btn_obtener_atacantes.config(state=tk.NORMAL, text="Obtener Lista")
        return

    inedito = var_inedito.get()
    mega = var_mega.get()
    oscuro = var_oscuro.get()
    legendario = var_legendario.get()

    if not (inedito or mega or oscuro or legendario):
        messagebox.showwarning("Aviso", "Activa al menos un filtro.")
        btn_obtener_atacantes.config(state=tk.NORMAL, text="Obtener Lista")
        return

    filtrados = filtrar_atacantes(datos, inedito, mega, oscuro, legendario)

    if not filtrados:
        messagebox.showwarning("Aviso", "No se encontraron Pokemon con esos filtros.")
        btn_obtener_atacantes.config(state=tk.NORMAL, text="Obtener Lista")
        return

    texto_cant = txt_cantidad.get().strip()
    if texto_cant.isdigit() and int(texto_cant) > 0:
        cantidad = int(texto_cant)
    else:
        cantidad = len(filtrados)
    cantidad = min(cantidad, len(filtrados))

    generar_cadena_atacantes(filtrados, cantidad)


def copiar_tab2():
    contenido = output_atacantes.get_text().strip()
    if contenido:
        ventana.clipboard_clear()
        ventana.clipboard_append(contenido)
        messagebox.showinfo("Copiado", "Cadena copiada al portapapeles con exito!")
    else:
        messagebox.showwarning("Aviso", "No hay nada que copiar todavia.")


def limpiar_tab2():
    output_atacantes.set_text("")
    output_atacantes.set_state(tk.DISABLED)


# ==========================================
# VENTANA PRINCIPAL
# ==========================================
ventana = tk.Tk()
ventana.title("PokeChain")
ventana.geometry("520x800")
ventana.minsize(480, 600)
ventana.configure(bg="#f0f0f0")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_icono = os.path.join(BASE_DIR, "icono.png")
if os.path.exists(_icono):
    img = tk.PhotoImage(file=_icono)
    ventana.iconphoto(True, img)

idioma = tk.StringVar(value="Español")


def _on_idioma_change(*args):
    _regenerar_tab1()
    _regenerar_tab2()


idioma.trace_add("write", _on_idioma_change)

frame_top = tk.Frame(ventana, bg="#f0f0f0")
frame_top.pack(fill=tk.X, padx=10, pady=(10, 0))

menu_idioma = ttk.OptionMenu(frame_top, idioma, "Español", "Español", "English")
menu_idioma.pack(side=tk.RIGHT)

notebook = ttk.Notebook(ventana)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# ==========================================
# PESTAÑA 1 — PVP
# ==========================================
tab1 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab1, text="  PVP  ")

frame_entrada_header = tk.Frame(tab1, bg="#f0f0f0")
frame_entrada_header.pack(anchor="w", padx=20, pady=(15, 5), fill=tk.X)

lbl_entrada = tk.Label(
    frame_entrada_header, text="1. Pega aqui tu lista de Pokemon:",
    bg="#f0f0f0", font=("Arial", 10, "bold"),
)
lbl_entrada.pack(side=tk.LEFT)

input_pokemon = TextInput(tab1, height=10, font=("Consolas", 10), wrap=tk.WORD)
input_pokemon.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
input_pokemon.text.bind("<Control-v>", lambda e: pegar_completo(e, input_pokemon))
input_pokemon.text.bind("<Control-V>", lambda e: pegar_completo(e, input_pokemon))

frame_acciones = tk.Frame(tab1, bg="#f0f0f0")
frame_acciones.pack(pady=10)

btn_procesar = tk.Button(
    frame_acciones, text="Convertir Lista", command=procesar_lista,
    bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_procesar.pack(side=tk.LEFT, padx=10)
Tooltip(btn_procesar, "Busca anteevoluciones en PokeAPI")

btn_limpiar = tk.Button(
    frame_acciones, text="Limpiar", command=limpiar_tab1,
    bg="#e0e0e0", fg="#333333", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_limpiar.pack(side=tk.LEFT, padx=10)

frame_progreso1 = tk.Frame(tab1, bg="#f0f0f0")

progress_bar1 = ttk.Progressbar(
    frame_progreso1, orient="horizontal", length=300, mode="determinate",
)
progress_bar1.pack(pady=(10, 2))

lbl_progreso1 = tk.Label(frame_progreso1, text="", bg="#f0f0f0", font=("Arial", 9))
lbl_progreso1.pack()

lbl_salida = tk.Label(
    tab1, text="2. Resultado ordenado por ID (Sin repetidos):",
    bg="#f0f0f0", font=("Arial", 10, "bold"),
)
lbl_salida.pack(anchor="w", padx=20, pady=(10, 5))

output_pokemon = TextInput(tab1, height=4, font=("Consolas", 10), wrap=tk.CHAR)
output_pokemon.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
output_pokemon.set_state(tk.DISABLED)

frame_ligas = tk.Frame(tab1, bg="#f0f0f0")
frame_ligas.pack(pady=(5, 0))

btn_great = tk.Button(
    frame_ligas, text="Great League", command=aplicar_great_league,
    bg="#7B68EE", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_great.pack(side=tk.LEFT, padx=10)
Tooltip(btn_great, "Anade filtro Great League (1500 CP)")

btn_ultra = tk.Button(
    frame_ligas, text="Ultra League", command=aplicar_ultra_league,
    bg="#FF8C00", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_ultra.pack(side=tk.LEFT, padx=10)
Tooltip(btn_ultra, "Anade filtro Ultra League (2500 CP)")

btn_copiar = tk.Button(
    tab1, text="Copiar al Portapapeles", command=copiar_tab1,
    bg="#008CBA", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_copiar.pack(pady=15)
Tooltip(btn_copiar, "Copia resultado al portapapeles")

# ==========================================
# PESTAÑA 2 — MEJORES ATACANTES
# ==========================================
tab2 = tk.Frame(notebook, bg="#f0f0f0")
notebook.add(tab2, text="  Atacantes  ")

var_inedito = tk.BooleanVar(value=False)
var_mega = tk.BooleanVar(value=False)
var_oscuro = tk.BooleanVar(value=True)
var_legendario = tk.BooleanVar(value=True)

frame_filtros = tk.LabelFrame(
    tab2, text="Filtros (aditivos)", bg="#f0f0f0",
    font=("Arial", 10, "bold"), padx=10, pady=8,
)
frame_filtros.pack(padx=20, pady=(15, 5), fill=tk.X)

chk_inedito = tk.Checkbutton(
    frame_filtros, text="Inedito", variable=var_inedito,
    bg="#f0f0f0", font=("Arial", 10),
)
chk_inedito.grid(row=0, column=0, sticky="w", padx=5)

chk_mega = tk.Checkbutton(
    frame_filtros, text="Mega / Primigenio", variable=var_mega,
    bg="#f0f0f0", font=("Arial", 10),
)
chk_mega.grid(row=0, column=1, sticky="w", padx=5)

chk_oscuro = tk.Checkbutton(
    frame_filtros, text="Oscuro", variable=var_oscuro,
    bg="#f0f0f0", font=("Arial", 10),
)
chk_oscuro.grid(row=1, column=0, sticky="w", padx=5)
Tooltip(chk_oscuro, "Incluye todas las formas Shadow-eligibles")

chk_legendario = tk.Checkbutton(
    frame_filtros, text="Legendario", variable=var_legendario,
    bg="#f0f0f0", font=("Arial", 10),
)
chk_legendario.grid(row=1, column=1, sticky="w", padx=5)
Tooltip(chk_legendario, "Incluye Legendary, Mythic y Ultra Beast")

frame_cantidad = tk.Frame(tab2, bg="#f0f0f0")
frame_cantidad.pack(padx=20, pady=5, fill=tk.X)

lbl_cantidad = tk.Label(
    frame_cantidad, text="N de Pokemon a incluir:",
    bg="#f0f0f0", font=("Arial", 10, "bold"),
)
lbl_cantidad.pack(side=tk.LEFT)

txt_cantidad = ttk.Entry(frame_cantidad, width=8, font=("Arial", 10))
txt_cantidad.insert(0, "200")
txt_cantidad.pack(side=tk.LEFT, padx=5)

btn_obtener_atacantes = tk.Button(
    tab2, text="Obtener Lista", command=obtener_lista_atacantes,
    bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5,
)
btn_obtener_atacantes.pack(pady=10)
Tooltip(btn_obtener_atacantes, "Descarga datos de DialgaDex y genera la cadena")

frame_progreso2 = tk.Frame(tab2, bg="#f0f0f0")

progress_bar2 = ttk.Progressbar(
    frame_progreso2, orient="horizontal", length=300, mode="determinate",
)
progress_bar2.pack(pady=(5, 2))

lbl_progreso2 = tk.Label(frame_progreso2, text="", bg="#f0f0f0", font=("Arial", 9))
lbl_progreso2.pack()

output_atacantes = TextInput(tab2, height=6, font=("Consolas", 10), wrap=tk.CHAR)
output_atacantes.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
output_atacantes.set_state(tk.DISABLED)

frame_acciones2 = tk.Frame(tab2, bg="#f0f0f0")
frame_acciones2.pack(pady=5)

btn_copiar2 = tk.Button(
    frame_acciones2, text="Copiar al Portapapeles", command=copiar_tab2,
    bg="#008CBA", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_copiar2.pack(side=tk.LEFT, padx=10)
Tooltip(btn_copiar2, "Copia resultado al portapapeles")

btn_limpiar2 = tk.Button(
    frame_acciones2, text="Limpiar", command=limpiar_tab2,
    bg="#e0e0e0", fg="#333333", font=("Arial", 10, "bold"), padx=10, pady=5,
)
btn_limpiar2.pack(side=tk.LEFT, padx=10)

ventana.mainloop()
