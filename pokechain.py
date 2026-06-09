import re
import tkinter as tk
from tkinter import messagebox, ttk
import os
import requests
from ttkthemes import ThemedTk


# ==========================================
# CONSTANTES
# ==========================================
DIALGADEX_URL = "https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_pkm.min.json"
PVPOKE_GAMEMASTER_URL = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/gamemaster.min.json"
PVPOKE_RANKINGS_URLS = {
    "Great League": "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/rankings/all/overall/rankings-1500.json",
    "Ultra League": "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/rankings/all/overall/rankings-2500.json",
}
PVPOKE_CP_CAPS = {
    "Great League": 1500,
    "Ultra League": 2500,
}
THEME_LIGHT = "arc"
THEME_DARK = "equilux"


# ==========================================
# TOOLTIP
# ==========================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def set_text(self, new_text):
        self.text = new_text

    def _show(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            tw, text=self.text, relief="solid", borderwidth=1, padding=(8, 4)
        )
        label.pack()

    def _hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def get_tooltip_text(var, texto_base):
    if var.get():
        return f"Incluye {texto_base}"
    return f"Excluye {texto_base}"


# ==========================================
# TEXTINPUT — Widget de texto robusto
# ==========================================
class TextInput(tk.Frame):
    def __init__(self, master, height=8, font=None, wrap=tk.WORD, **kwargs):
        super().__init__(master, **kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text = tk.Text(
            self,
            height=height,
            font=font or ("Consolas", 10),
            wrap=wrap,
            undo=False,
            yscrollcommand=self.scrollbar.set,
            borderwidth=0,
            highlightthickness=0,
            padx=6,
            pady=6,
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
# STATUSBAR
# ==========================================
class StatusBar(ttk.Frame):
    def __init__(self, container):
        super().__init__(container, relief=tk.SUNKEN)
        self.label = ttk.Label(self, text="Listo", anchor="w", padding=(5, 2))
        self.label.pack(fill="x")

    def set_message(self, msg):
        self.label.config(text=msg)

    def clear(self):
        self.label.config(text="Listo")


# ==========================================
# SHARED LOGIC (funciones puras)
# ==========================================
def get_prefijo_shadow(idioma):
    return "Shadow&" if idioma == "English" else "Oscuro&"


def criterio_ordenacion(elemento):
    match = re.search(r"\d+", elemento)
    if match:
        return int(match.group(0))
    return 0


def limpiar_nombre_especie(nombre):
    nombre = re.sub(r"^(Mega|Shadow)\s+", "", nombre)
    nombre = re.sub(r"\s+[XYZ]$", "", nombre)
    return nombre.strip()


def analizar_nombre(nombre_sucio, idioma):
    es_shadow = re.search(r"\(Shadow\)", nombre_sucio, re.IGNORECASE) or \
                re.search(r"\(Oscuro\)", nombre_sucio, re.IGNORECASE)
    prefijo = get_prefijo_shadow(idioma) if es_shadow else ""
    nombre_limpio = re.sub(r"\s*\(.*?\)", "", nombre_sucio)
    return nombre_limpio.strip().lower(), prefijo


def analizar_raw(nombre_sucio):
    es_shadow = bool(re.search(r"\(Shadow\)|\(Oscuro\)", nombre_sucio, re.IGNORECASE))
    nombre_limpio = re.sub(r"\s*\(.*?\)", "", nombre_sucio).strip().lower()
    return nombre_limpio, es_shadow


# ==========================================
# API CACHE
# ==========================================
class ApiCache:
    def __init__(self):
        self._cache_especie = {}
        self._cache_dialgadex = None
        self._cache_gamemaster = None
        self._cache_rankings = {}
        self._session = requests.Session()
        self._timeout = 15

    def consulta_api(self, url):
        clave = url.lower()
        if clave in self._cache_especie:
            return self._cache_especie[clave]
        try:
            r = self._session.get(url, timeout=self._timeout)
            if r.status_code == 200:
                self._cache_especie[clave] = r.json()
                return self._cache_especie[clave]
        except Exception:
            pass
        return None

    def descargar_dialgadex(self):
        if self._cache_dialgadex is not None:
            return self._cache_dialgadex
        try:
            r = self._session.get(DIALGADEX_URL, timeout=30)
            if r.status_code == 200:
                self._cache_dialgadex = r.json()
                return self._cache_dialgadex
        except Exception:
            pass
        return None

    def descargar_gamemaster(self):
        if self._cache_gamemaster is None:
            try:
                r = self._session.get(PVPOKE_GAMEMASTER_URL, timeout=self._timeout)
                if r.status_code == 200:
                    self._cache_gamemaster = r.json()
            except Exception:
                pass
        return self._cache_gamemaster

    def descargar_rankings(self, liga):
        if liga in self._cache_rankings:
            return self._cache_rankings[liga]
        url = PVPOKE_RANKINGS_URLS.get(liga)
        if not url:
            return None
        try:
            r = self._session.get(url, timeout=self._timeout)
            if r.status_code == 200:
                self._cache_rankings[liga] = r.json()
                return self._cache_rankings[liga]
        except Exception:
            pass
        return None

    def buscar_anteevolucion(self, nombre):
        url = f"https://pokeapi.co/api/v2/pokemon-species/{nombre.lower().strip()}/"
        datos = self.consulta_api(url)
        if not datos:
            return None
        while datos.get("evolves_from_species"):
            padre = self.consulta_api(datos["evolves_from_species"]["url"])
            if not padre:
                break
            datos = padre
        return str(datos["id"])


# ==========================================
# PESTAÑA 1 — PVP
# ==========================================
class PvPokeTab(ttk.Frame):
    def __init__(self, container, api_cache, idioma_var, status_bar):
        super().__init__(container)
        self.api = api_cache
        self.idioma_var = idioma_var
        self.status_bar = status_bar
        self._cache_ids = None
        self._prefijo_liga = ""
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        # Filtros
        frame_filtros = ttk.LabelFrame(self, text="Filtros (aditivos)", padding=10)
        frame_filtros.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        frame_filtros.columnconfigure(0, weight=1)
        frame_filtros.columnconfigure(1, weight=1)
        frame_filtros.columnconfigure(2, weight=1)

        self.var_mt = tk.BooleanVar(value=True)
        self.var_oscuro = tk.BooleanVar(value=True)
        self.var_xl = tk.BooleanVar(value=True)

        chk_mt = ttk.Checkbutton(frame_filtros, text="MT de Élite", variable=self.var_mt)
        chk_mt.grid(row=0, column=0, sticky="w", padx=5)
        self.tooltip_mt = ToolTip(chk_mt, get_tooltip_text(self.var_mt, "Pokemon que requieren MT de Élite"))
        self.var_mt.trace_add("write", lambda *a: self.tooltip_mt.set_text(get_tooltip_text(self.var_mt, "Pokemon que requieren MT de Élite")))

        chk_oscuro = ttk.Checkbutton(frame_filtros, text="Oscuro", variable=self.var_oscuro)
        chk_oscuro.grid(row=0, column=1, sticky="w", padx=5)
        self.tooltip_oscuro = ToolTip(chk_oscuro, get_tooltip_text(self.var_oscuro, "Pokemon Shadow"))
        self.var_oscuro.trace_add("write", lambda *a: self.tooltip_oscuro.set_text(get_tooltip_text(self.var_oscuro, "Pokemon Shadow")))

        chk_xl = ttk.Checkbutton(frame_filtros, text="Caramelos XL", variable=self.var_xl)
        chk_xl.grid(row=0, column=2, sticky="w", padx=5)
        self.tooltip_xl = ToolTip(chk_xl, get_tooltip_text(self.var_xl, "Pokemon que necesitan XL para alcanzar el CP cap"))
        self.var_xl.trace_add("write", lambda *a: self.tooltip_xl.set_text(get_tooltip_text(self.var_xl, "Pokemon que necesitan XL para alcanzar el CP cap")))

        # Cantidad
        frame_cantidad = ttk.Frame(self)
        frame_cantidad.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        lbl_cantidad = ttk.Label(frame_cantidad, text="N de Pokemon a incluir:")
        lbl_cantidad.pack(side=tk.LEFT)

        self.txt_cantidad = ttk.Entry(frame_cantidad, width=8)
        self.txt_cantidad.insert(0, "200")
        self.txt_cantidad.pack(side=tk.LEFT, padx=5)

        # Botones de liga
        frame_botones = ttk.Frame(self)
        frame_botones.grid(row=2, column=0, pady=10)

        self.btn_great = ttk.Button(
            frame_botones, text="Great League",
            command=lambda: self._obtener_lista_pvp("Great League")
        )
        self.btn_great.pack(side=tk.LEFT, padx=10)

        self.btn_ultra = ttk.Button(
            frame_botones, text="Ultra League",
            command=lambda: self._obtener_lista_pvp("Ultra League")
        )
        self.btn_ultra.pack(side=tk.LEFT, padx=10)

        # Barra de progreso
        self.frame_progreso = ttk.Frame(self)

        self.progress_bar = ttk.Progressbar(
            self.frame_progreso, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=(10, 2))

        self.lbl_progreso = ttk.Label(self.frame_progreso, text="")
        self.lbl_progreso.pack()

        # Resultado
        self.output = TextInput(self, height=8, font=("Consolas", 10), wrap=tk.CHAR)
        self.output.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        self.output.set_state(tk.DISABLED)

        # Acciones
        frame_acciones = ttk.Frame(self)
        frame_acciones.grid(row=6, column=0, pady=5)

        btn_copiar = ttk.Button(frame_acciones, text="Copiar al Portapapeles", command=self._copiar)
        btn_copiar.pack(side=tk.LEFT, padx=10)

        btn_limpiar = ttk.Button(frame_acciones, text="Limpiar", command=self._limpiar)
        btn_limpiar.pack(side=tk.LEFT, padx=10)

    def _regenerar(self):
        if self._cache_ids is None:
            return
        idioma = self.idioma_var.get()
        prefijo_shadow = get_prefijo_shadow(idioma)
        items = []
        for id_num, es_shadow in self._cache_ids:
            pref = prefijo_shadow if es_shadow else ""
            items.append(f"{pref}+{id_num}")
        lista_ordenada = sorted(items, key=criterio_ordenacion)
        cadena_ids = ";".join(lista_ordenada)
        resultado = self._prefijo_liga + cadena_ids + "&!#" if self._prefijo_liga else cadena_ids + "&!#"
        self.output.set_text(resultado)
        self.output.set_state(tk.DISABLED)

    def _obtener_lista_pvp(self, liga):
        idioma = self.idioma_var.get()
        self.btn_great.config(state=tk.DISABLED)
        self.btn_ultra.config(state=tk.DISABLED)
        self.frame_progreso.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar["value"] = 0
        self.status_bar.set_message(f"Descargando datos de {liga}...")
        self.update_idletasks()

        gamemaster = self.api.descargar_gamemaster()
        if not gamemaster:
            messagebox.showerror("Error", "No se pudieron descargar los datos de PvPoke.")
            self.btn_great.config(state=tk.NORMAL)
            self.btn_ultra.config(state=tk.NORMAL)
            self.frame_progreso.grid_forget()
            self.status_bar.clear()
            return

        rankings = self.api.descargar_rankings(liga)
        if not rankings:
            messagebox.showerror("Error", f"No se pudieron descargar los rankings de {liga}.")
            self.btn_great.config(state=tk.NORMAL)
            self.btn_ultra.config(state=tk.NORMAL)
            self.frame_progreso.grid_forget()
            self.status_bar.clear()
            return

        mt_elite = self.var_mt.get()
        oscuro = self.var_oscuro.get()
        xl = self.var_xl.get()

        filtrados = self._filtrar_pvpoke(gamemaster, rankings, liga, mt_elite, oscuro, xl)

        if not filtrados:
            messagebox.showwarning("Aviso", "No se encontraron Pokemon con esos filtros.")
            self.btn_great.config(state=tk.NORMAL)
            self.btn_ultra.config(state=tk.NORMAL)
            self.frame_progreso.grid_forget()
            self.status_bar.clear()
            return

        texto_cant = self.txt_cantidad.get().strip()
        if texto_cant.isdigit() and int(texto_cant) > 0:
            cantidad = int(texto_cant)
        else:
            cantidad = len(filtrados)
        cantidad = min(cantidad, len(filtrados))

        top = filtrados[:cantidad]
        total = len(top)
        self.progress_bar["maximum"] = total
        self._cache_ids = set()

        cp_cap = PVPOKE_CP_CAPS.get(liga, 1500)
        if idioma == "English":
            self._prefijo_liga = f"cp-{cp_cap}&-1attack&3-defense&3-hp&"
        else:
            self._prefijo_liga = f"PC-{cp_cap}&3-4puntos de salud&3-4defensa&0-1ataque&"

        self.status_bar.set_message(f"Procesando {total} Pokemon...")

        for i, p in enumerate(top):
            nombre = limpiar_nombre_especie(p["speciesName"])
            resultado = self._obtener_id_raw(nombre)
            if resultado:
                self._cache_ids.add(resultado)
            self.progress_bar["value"] = i + 1
            self.lbl_progreso.config(text=f"{i+1}/{total} ({100*(i+1)//total}%)")
            self.update_idletasks()

        self._regenerar()

        self.btn_great.config(state=tk.NORMAL)
        self.btn_ultra.config(state=tk.NORMAL)
        self.frame_progreso.grid_forget()
        self.status_bar.set_message(f"Completado: {total} Pokemon procesados")

    def _filtrar_pvpoke(self, gamemaster, rankings, liga, mt_elite, oscuro, xl):
        cp_cap = PVPOKE_CP_CAPS.get(liga, 1500)
        gm_by_name = {}
        for p in gamemaster.get("pokemon", []):
            gm_by_name[p["speciesName"]] = p
            gm_by_name[p["speciesId"]] = p
        resultado = []
        for r in rankings:
            nombre = r["speciesName"]
            es_shadow = "(Shadow)" in nombre or "shadow" in nombre.lower()
            nombre_limpio = re.sub(r"\s*\(Shadow\)", "", nombre).strip()
            gm = gm_by_name.get(nombre_limpio) or gm_by_name.get(
                nombre.lower().replace(" ", "_").replace(" (shadow)", "")
            )
            if es_shadow and not oscuro:
                continue
            if not mt_elite and gm:
                elite_moves = set(gm.get("eliteMoves", []))
                moveset = set(r.get("moveset", []))
                if elite_moves & moveset:
                    continue
            if not xl and gm:
                l25 = gm.get("level25CP", 9999)
                if l25 < cp_cap:
                    continue
            resultado.append(r)
        return resultado

    def _obtener_id_raw(self, nombre_pokemon):
        idioma = self.idioma_var.get()
        nombre, es_shadow = analizar_raw(nombre_pokemon)
        if not nombre:
            return None
        datos_especie = self.api.consulta_api(
            f"https://pokeapi.co/api/v2/pokemon-species/{nombre}/"
        )
        if not datos_especie:
            return None
        while datos_especie.get("evolves_from_species"):
            padre = self.api.consulta_api(datos_especie["evolves_from_species"]["url"])
            if not padre:
                break
            datos_especie = padre
        return (datos_especie["id"], es_shadow)

    def _copiar(self):
        contenido = self.output.get_text().strip()
        if contenido:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(contenido)
            messagebox.showinfo("Copiado", "Cadena copiada al portapapeles con exito!")
        else:
            messagebox.showwarning("Aviso", "No hay nada que copiar todavia.")

    def _limpiar(self):
        self.output.set_text("")
        self.output.set_state(tk.DISABLED)

    def on_idioma_change(self):
        self._regenerar()


# ==========================================
# PESTAÑA 2 — DIALGADEX
# ==========================================
class DialgadexTab(ttk.Frame):
    def __init__(self, container, api_cache, idioma_var, status_bar):
        super().__init__(container)
        self.api = api_cache
        self.idioma_var = idioma_var
        self.status_bar = status_bar
        self._cache_ids = None
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        # Filtros
        frame_filtros = ttk.LabelFrame(self, text="Filtros (aditivos)", padding=10)
        frame_filtros.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        frame_filtros.columnconfigure(0, weight=1)
        frame_filtros.columnconfigure(1, weight=1)

        self.var_inedito = tk.BooleanVar(value=False)
        self.var_mega = tk.BooleanVar(value=False)
        self.var_oscuro = tk.BooleanVar(value=True)
        self.var_legendario = tk.BooleanVar(value=True)

        chk_inedito = ttk.Checkbutton(frame_filtros, text="Inedito", variable=self.var_inedito)
        chk_inedito.grid(row=0, column=0, sticky="w", padx=5)
        self.tooltip_inedito = ToolTip(chk_inedito, get_tooltip_text(self.var_inedito, "Pokemon no lanzados"))
        self.var_inedito.trace_add("write", lambda *a: self.tooltip_inedito.set_text(get_tooltip_text(self.var_inedito, "Pokemon no lanzados")))

        chk_mega = ttk.Checkbutton(frame_filtros, text="Mega / Primigenio", variable=self.var_mega)
        chk_mega.grid(row=0, column=1, sticky="w", padx=5)
        self.tooltip_mega = ToolTip(chk_mega, get_tooltip_text(self.var_mega, "Pokemon Mega y Primigenio"))
        self.var_mega.trace_add("write", lambda *a: self.tooltip_mega.set_text(get_tooltip_text(self.var_mega, "Pokemon Mega y Primigenio")))

        chk_oscuro = ttk.Checkbutton(frame_filtros, text="Oscuro", variable=self.var_oscuro)
        chk_oscuro.grid(row=1, column=0, sticky="w", padx=5)
        self.tooltip_oscuro = ToolTip(chk_oscuro, get_tooltip_text(self.var_oscuro, "todas las formas Shadow-eligibles"))
        self.var_oscuro.trace_add("write", lambda *a: self.tooltip_oscuro.set_text(get_tooltip_text(self.var_oscuro, "todas las formas Shadow-eligibles")))

        chk_legendario = ttk.Checkbutton(frame_filtros, text="Legendario", variable=self.var_legendario)
        chk_legendario.grid(row=1, column=1, sticky="w", padx=5)
        self.tooltip_legendario = ToolTip(chk_legendario, get_tooltip_text(self.var_legendario, "Legendary, Mythic y Ultra Beast"))
        self.var_legendario.trace_add("write", lambda *a: self.tooltip_legendario.set_text(get_tooltip_text(self.var_legendario, "Legendary, Mythic y Ultra Beast")))

        # Cantidad
        frame_cantidad = ttk.Frame(self)
        frame_cantidad.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        lbl_cantidad = ttk.Label(frame_cantidad, text="N de Pokemon a incluir:")
        lbl_cantidad.pack(side=tk.LEFT)

        self.txt_cantidad = ttk.Entry(frame_cantidad, width=8)
        self.txt_cantidad.insert(0, "200")
        self.txt_cantidad.pack(side=tk.LEFT, padx=5)

        # Boton obtener
        self.btn_obtener = ttk.Button(
            self, text="Obtener Lista", command=self._obtener_lista_atacantes
        )
        self.btn_obtener.grid(row=2, column=0, pady=10)

        # Barra de progreso
        self.frame_progreso = ttk.Frame(self)

        self.progress_bar = ttk.Progressbar(
            self.frame_progreso, orient="horizontal", length=300, mode="determinate"
        )
        self.progress_bar.pack(pady=(5, 2))

        self.lbl_progreso = ttk.Label(self.frame_progreso, text="")
        self.lbl_progreso.pack()

        # Resultado
        self.output = TextInput(self, height=8, font=("Consolas", 10), wrap=tk.CHAR)
        self.output.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        self.output.set_state(tk.DISABLED)

        # Acciones
        frame_acciones = ttk.Frame(self)
        frame_acciones.grid(row=6, column=0, pady=5)

        btn_copiar = ttk.Button(frame_acciones, text="Copiar al Portapapeles", command=self._copiar)
        btn_copiar.pack(side=tk.LEFT, padx=10)

        btn_limpiar = ttk.Button(frame_acciones, text="Limpiar", command=self._limpiar)
        btn_limpiar.pack(side=tk.LEFT, padx=10)

    def _regenerar(self):
        if self._cache_ids is None:
            return
        idioma = self.idioma_var.get()
        prefijo_shadow = get_prefijo_shadow(idioma)
        prefijo_calidad = "4*,3*&3-attack&" if idioma == "English" else "4*;3*&3-ataque&"
        items = []
        for id_base, es_shadow in self._cache_ids:
            pref = prefijo_shadow if es_shadow else ""
            items.append(f"{pref}+{id_base}")
        lista_ordenada = sorted(items, key=criterio_ordenacion)
        resultado = prefijo_calidad + ";".join(lista_ordenada) + "&!#"
        self.output.set_text(resultado)
        self.output.set_state(tk.DISABLED)

    def _filtrar_atacantes(self, datos, inedito, mega, oscuro, legendario):
        resultado = []
        for p in datos:
            incluir = False
            es_normal = (
                p.get("class") is None
                and not p.get("shadow", False)
                and p.get("form", "Normal") == "Normal"
                and p.get("released", False)
            )
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

    def _generar_cadena(self, lista_pokemon, cantidad):
        self.btn_obtener.config(state=tk.DISABLED)
        self.frame_progreso.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar["value"] = 0
        self.status_bar.set_message("Generando cadena de busqueda...")
        self.update_idletasks()

        top = lista_pokemon[:cantidad]
        total = len(top)
        self.progress_bar["maximum"] = total
        self._cache_ids = set()

        for i, p in enumerate(top):
            nombre = limpiar_nombre_especie(p["name"])
            es_shadow = p.get("shadow", False)

            id_base = self.api.buscar_anteevolucion(nombre)
            if not id_base:
                id_base = p["id"]

            self._cache_ids.add((int(id_base), es_shadow))

            self.progress_bar["value"] = i + 1
            self.lbl_progreso.config(text=f"{i+1}/{total} ({100*(i+1)//total}%)")
            self.update_idletasks()

        self._regenerar()

        self.btn_obtener.config(state=tk.NORMAL)
        self.frame_progreso.grid_forget()
        self.status_bar.set_message(f"Completado: {total} Pokemon procesados")

    def _obtener_lista_atacantes(self):
        self.btn_obtener.config(state=tk.DISABLED)
        self.status_bar.set_message("Descargando datos de DialgaDex...")
        self.update_idletasks()

        datos = self.api.descargar_dialgadex()
        if not datos:
            messagebox.showerror("Error", "No se pudieron descargar los datos de DialgaDex.")
            self.btn_obtener.config(state=tk.NORMAL)
            self.status_bar.clear()
            return

        inedito = self.var_inedito.get()
        mega = self.var_mega.get()
        oscuro = self.var_oscuro.get()
        legendario = self.var_legendario.get()

        if not (inedito or mega or oscuro or legendario):
            messagebox.showwarning("Aviso", "Activa al menos un filtro.")
            self.btn_obtener.config(state=tk.NORMAL)
            self.status_bar.clear()
            return

        filtrados = self._filtrar_atacantes(datos, inedito, mega, oscuro, legendario)

        if not filtrados:
            messagebox.showwarning("Aviso", "No se encontraron Pokemon con esos filtros.")
            self.btn_obtener.config(state=tk.NORMAL)
            self.status_bar.clear()
            return

        texto_cant = self.txt_cantidad.get().strip()
        if texto_cant.isdigit() and int(texto_cant) > 0:
            cantidad = int(texto_cant)
        else:
            cantidad = len(filtrados)
        cantidad = min(cantidad, len(filtrados))

        self._generar_cadena(filtrados, cantidad)

    def _copiar(self):
        contenido = self.output.get_text().strip()
        if contenido:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(contenido)
            messagebox.showinfo("Copiado", "Cadena copiada al portapapeles con exito!")
        else:
            messagebox.showwarning("Aviso", "No hay nada que copiar todavia.")

    def _limpiar(self):
        self.output.set_text("")
        self.output.set_state(tk.DISABLED)

    def on_idioma_change(self):
        self._regenerar()


# ==========================================
# VENTANA PRINCIPAL
# ==========================================
class PokeChainApp(ThemedTk):
    def __init__(self):
        super().__init__(themebg=True)
        self.set_theme(THEME_LIGHT)
        self.title("PokeChain")
        self.geometry("600x850")
        self.minsize(520, 700)

        self.dark_mode = False
        self.idioma = tk.StringVar(value="Español")

        # API Cache compartido
        self.api_cache = ApiCache()

        # Icono
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        _icono = os.path.join(BASE_DIR, "icono.png")
        if os.path.exists(_icono):
            img = tk.PhotoImage(file=_icono)
            self.iconphoto(True, img)

        # Crear UI
        self._create_menu()
        self._create_header()
        self._create_status_bar()
        self._create_notebook()

        # Atajos de teclado
        self._bind_shortcuts()

        # Trace de idioma
        self.idioma.trace_add("write", self._on_idioma_change)

    def _create_menu(self):
        menubar = tk.Menu(self)

        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ver = tk.Menu(menubar, tearoff=0)
        menu_ver.add_command(label="Cambiar tema (Oscuro/Claro)", command=self._toggle_theme)
        menu_ver.add_separator()
        menu_ver.add_command(label="PvPoke (Ctrl+1)", command=lambda: self.notebook.select(0))
        menu_ver.add_command(label="Dialgadex (Ctrl+2)", command=lambda: self.notebook.select(1))
        menubar.add_cascade(label="Ver", menu=menu_ver)

        menu_idioma = tk.Menu(menubar, tearoff=0)
        menu_idioma.add_command(label="Espanol", command=lambda: self.idioma.set("Español"))
        menu_idioma.add_command(label="English", command=lambda: self.idioma.set("English"))
        menubar.add_cascade(label="Idioma", menu=menu_idioma)

        self.config(menu=menubar)

    def _create_header(self):
        frame_top = ttk.Frame(self)
        frame_top.pack(fill=tk.X, padx=10, pady=(10, 0))

        lbl_idioma = ttk.Label(frame_top, text="Idioma:")
        lbl_idioma.pack(side=tk.LEFT)

        menu_idioma = ttk.OptionMenu(frame_top, self.idioma, "Español", "Español", "English")
        menu_idioma.pack(side=tk.LEFT, padx=5)

        btn_tema = ttk.Button(frame_top, text="Cambiar tema", command=self._toggle_theme)
        btn_tema.pack(side=tk.RIGHT)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab1 = PvPokeTab(self.notebook, self.api_cache, self.idioma, self._status_bar)
        self.tab2 = DialgadexTab(self.notebook, self.api_cache, self.idioma, self._status_bar)

        self.notebook.add(self.tab1, text="  PvPoke  ")
        self.notebook.add(self.tab2, text="  Dialgadex  ")

    def _create_status_bar(self):
        self._status_bar = StatusBar(self)
        self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self):
        self.bind_all("<Control-Key-1>", lambda e: self.notebook.select(0))
        self.bind_all("<Control-Key-2>", lambda e: self.notebook.select(1))
        self.bind("<Control-t>", lambda e: self._toggle_theme())
        self.bind("<Control-q>", lambda e: self.destroy())

    def _toggle_theme(self):
        if self.dark_mode:
            self.set_theme(THEME_LIGHT)
        else:
            self.set_theme(THEME_DARK)
        self.dark_mode = not self.dark_mode
        self._status_bar.set_message("Tema cambiado a " + ("Claro" if not self.dark_mode else "Oscuro"))

    def _on_idioma_change(self, *args):
        self.tab1.on_idioma_change()
        self.tab2.on_idioma_change()
        self._status_bar.set_message("Idioma cambiado a " + self.idioma.get())


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    app = PokeChainApp()
    app.mainloop()
