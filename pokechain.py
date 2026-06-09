import io
import math
import re
import tkinter as tk
from tkinter import messagebox, ttk
import os
import requests
import PIL.Image
import PIL.ImageDraw


# ==========================================
# CONSTANTES
# ==========================================
DIALGADEX_URL = "https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_pkm.min.json"
FAST_MOVES_URL = "https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_fm.json"
CHARGED_MOVES_URL = "https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_cm.json"
PVPOKE_GAMEMASTER_URL = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/gamemaster.min.json"
PVPOKE_RANKINGS_URLS = {
    "Great League": "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/rankings/all/overall/rankings-1500.json",
    "Ultra League": "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/rankings/all/overall/rankings-2500.json",
    "Master League": "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/rankings/all/overall/rankings-10000.json",
}
PVPOKE_CP_CAPS = {
    "Great League": 1500,
    "Ultra League": 2500,
    "Master League": None,
}

POKEMON_TYPES = {
    "Normal", "Fire", "Water", "Grass", "Electric", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy",
}

TYPE_EFFECTIVENESS = {
    "Normal":   (["Ghost"], ["Rock", "Steel"], []),
    "Fire":     ([], ["Dragon", "Fire", "Rock", "Water"], ["Bug", "Grass", "Ice", "Steel"]),
    "Water":    ([], ["Dragon", "Grass", "Water"], ["Fire", "Ground", "Rock"]),
    "Grass":    ([], ["Bug", "Dragon", "Fire", "Flying", "Grass", "Poison", "Steel"], ["Ground", "Rock", "Water"]),
    "Electric": (["Ground"], ["Dragon", "Electric", "Grass"], ["Flying", "Water"]),
    "Ice":      ([], ["Fire", "Ice", "Steel", "Water"], ["Dragon", "Flying", "Grass", "Ground"]),
    "Fighting": (["Ghost"], ["Bug", "Fairy", "Flying", "Poison", "Psychic"], ["Dark", "Ice", "Normal", "Rock", "Steel"]),
    "Poison":   (["Steel"], ["Ghost", "Ground", "Poison", "Rock"], ["Fairy", "Grass"]),
    "Ground":   (["Flying"], ["Bug", "Grass"], ["Electric", "Fire", "Poison", "Rock", "Steel"]),
    "Flying":   ([], ["Electric", "Rock", "Steel"], ["Bug", "Fighting", "Grass"]),
    "Psychic":  (["Dark"], ["Psychic", "Steel"], ["Fighting", "Poison"]),
    "Bug":      ([], ["Fairy", "Fighting", "Fire", "Flying", "Ghost", "Poison", "Steel"], ["Dark", "Grass", "Psychic"]),
    "Rock":     ([], ["Fighting", "Ground", "Steel"], ["Bug", "Fire", "Flying", "Ice"]),
    "Ghost":    (["Normal"], ["Dark"], ["Ghost", "Psychic"]),
    "Dragon":   (["Fairy"], ["Steel"], ["Dragon"]),
    "Dark":     ([], ["Dark", "Fairy", "Fighting"], ["Ghost", "Psychic"]),
    "Steel":    ([], ["Electric", "Fire", "Steel", "Water"], ["Fairy", "Ice", "Rock"]),
    "Fairy":    ([], ["Fire", "Poison", "Steel"], ["Dark", "Dragon", "Fighting"]),
}

CPM_LEVEL_40 = 0.7903
CPM_LEVEL_50 = 0.8403

RAID_TIER_HP = {1: 600, 2: 600, 3: 3600, 4: 9000, 5: 15000, 6: 22500}
RAID_TIER_CPM = {1: 0.6, 2: 0.67, 3: 0.73, 4: 0.79, 5: 0.79, 6: 1.0}

ESTIMATED_Y_NUMERATOR = 1970
ESTIMATED_CM_POWER = 11670

LIGHT_COLORS = {
    'bg': '#f0f4f8',
    'surface': '#ffffff',
    'fg': '#1a202c',
    'fg_secondary': '#4a5568',
    'primary': '#3182ce',
    'primary_hover': '#2b6cb0',
    'primary_active': '#2c5282',
    'success': '#38a169',
    'success_hover': '#2f855a',
    'warning': '#dd6b20',
    'warning_hover': '#c05621',
    'danger': '#e53e3e',
    'danger_hover': '#c53030',
    'accent': '#4299e1',
    'border': '#e2e8f0',
    'tab_selected': '#3182ce',
    'tab_normal': '#e2e8f0',
    'great_league': '#3B82F6',
    'great_league_hover': '#2563EB',
    'ultra_league': '#FFC107',
    'ultra_league_hover': '#FFB300',
    'master_league': '#9B59B6',
    'master_league_hover': '#7B2D8E',
    'toggle_on': '#38a169',
    'toggle_off': '#cbd5e0',
    'toggle_knob': '#ffffff',
}

DARK_COLORS = {
    'bg': '#1a202c',
    'surface': '#2d3748',
    'fg': '#f7fafc',
    'fg_secondary': '#a0aec0',
    'primary': '#4299e1',
    'primary_hover': '#3182ce',
    'primary_active': '#2b6cb0',
    'success': '#48bb78',
    'success_hover': '#38a169',
    'warning': '#ed8936',
    'warning_hover': '#dd6b20',
    'danger': '#fc8181',
    'danger_hover': '#e53e3e',
    'accent': '#63b3ed',
    'border': '#4a5568',
    'tab_selected': '#4299e1',
    'tab_normal': '#4a5568',
    'great_league': '#60A5FA',
    'great_league_hover': '#3B82F6',
    'ultra_league': '#FFD54F',
    'ultra_league_hover': '#FFC107',
    'master_league': '#A66DD4',
    'master_league_hover': '#9B59B6',
    'toggle_on': '#48bb78',
    'toggle_off': '#4a5568',
    'toggle_knob': '#ffffff',
}


# ==========================================
# THEME ENGINE
# ==========================================
def apply_theme(style, colors):
    style.theme_use('clam')

    style.configure('.', background=colors['bg'], foreground=colors['fg'],
                     font=('Segoe UI', 10))

    style.configure('TFrame', background=colors['bg'])
    style.configure('Surface.TFrame', background=colors['surface'])

    style.configure('TLabel', background=colors['bg'], foreground=colors['fg'],
                     font=('Segoe UI', 10))
    style.configure('Secondary.TLabel', foreground=colors['fg_secondary'])
    style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'),
                     foreground=colors['fg'])
    style.configure('Status.TLabel', background=colors['surface'],
                     foreground=colors['fg_secondary'], font=('Segoe UI', 9))

    style.configure('TLabelframe', background=colors['bg'],
                     foreground=colors['fg'], bordercolor=colors['border'],
                     relief='groove')
    style.configure('TLabelframe.Label', background=colors['bg'],
                     foreground=colors['fg'], font=('Segoe UI', 10, 'bold'))

    style.configure('TButton', background=colors['primary'], foreground='white',
                     font=('Segoe UI', 10, 'bold'), padding=(14, 7),
                     borderwidth=0, relief='flat')
    style.map('TButton',
              background=[('active', colors['primary_hover']),
                          ('pressed', colors['primary_active']),
                          ('disabled', colors['border'])],
              foreground=[('disabled', colors['fg_secondary'])])

    style.configure('Success.TButton', background=colors['success'], foreground='white')
    style.map('Success.TButton',
              background=[('active', colors['success_hover']),
                          ('pressed', colors['success_hover'])])

    style.configure('Warning.TButton', background=colors['warning'], foreground='white')
    style.map('Warning.TButton',
              background=[('active', colors['warning_hover']),
                          ('pressed', colors['warning_hover'])])

    style.configure('Danger.TButton', background=colors['danger'], foreground='white')
    style.map('Danger.TButton',
              background=[('active', colors['danger_hover']),
                          ('pressed', colors['danger_hover'])])

    style.configure('Surface.TButton', background=colors['surface'],
                     foreground=colors['fg'], bordercolor=colors['border'])
    style.map('Surface.TButton',
              background=[('active', colors['border'])])

    style.configure('Great.TButton', background=colors['great_league'], foreground='white',
                     font=('Segoe UI', 10, 'bold'), padding=(14, 7),
                     borderwidth=0, relief='flat')
    style.map('Great.TButton',
              background=[('active', colors['great_league_hover']),
                          ('pressed', colors['great_league_hover']),
                          ('disabled', colors['border'])],
              foreground=[('disabled', colors['fg_secondary'])])

    style.configure('Ultra.TButton', background=colors['ultra_league'], foreground='#1a202c',
                     font=('Segoe UI', 10, 'bold'), padding=(14, 7),
                     borderwidth=0, relief='flat')
    style.map('Ultra.TButton',
              background=[('active', colors['ultra_league_hover']),
                          ('pressed', colors['ultra_league_hover']),
                          ('disabled', colors['border'])],
              foreground=[('disabled', colors['fg_secondary'])])

    style.configure('Master.TButton', background=colors['master_league'], foreground='white',
                     font=('Segoe UI', 10, 'bold'), padding=(14, 7),
                     borderwidth=0, relief='flat')
    style.map('Master.TButton',
              background=[('active', colors['master_league_hover']),
                          ('pressed', colors['master_league_hover']),
                          ('disabled', colors['border'])],
              foreground=[('disabled', colors['fg_secondary'])])

    style.configure('TEntry', fieldbackground=colors['surface'],
                     foreground=colors['fg'], bordercolor=colors['border'],
                     insertcolor=colors['fg'], padding=6)
    style.map('TEntry',
              fieldbackground=[('focus', colors['surface'])],
              bordercolor=[('focus', colors['primary'])])

    style.configure('TCheckbutton', background=colors['bg'],
                     foreground=colors['fg'], indicatorcolor=colors['surface'],
                     indicatorsize=18, padding=6)
    style.map('TCheckbutton',
              indicatorcolor=[('selected', colors['primary'])],
              background=[('active', colors['bg'])])

    style.configure('TRadiobutton', background=colors['bg'],
                     foreground=colors['fg'], indicatorcolor=colors['surface'],
                     indicatorsize=18, padding=6)
    style.map('TRadiobutton',
              indicatorcolor=[('selected', colors['primary'])])

    style.configure('TNotebook', background=colors['bg'], borderwidth=0)
    style.configure('TNotebook.Tab', background=colors['tab_normal'],
                     foreground=colors['fg'], padding=[16, 6],
                     font=('Segoe UI', 10, 'bold'))
    style.map('TNotebook.Tab',
              background=[('selected', colors['tab_selected']),
                          ('!selected', colors['tab_normal'])],
              foreground=[('selected', 'white'),
                          ('!selected', colors['fg'])],
              padding=[('selected', [16, 6]),
                       ('!selected', [16, 6])])

    style.configure('Horizontal.TProgressbar', background=colors['primary'],
                     troughcolor=colors['surface'], borderwidth=0,
                     thickness=20)

    style.configure('TScrollbar', background=colors['border'],
                     troughcolor=colors['surface'], borderwidth=0,
                     arrowsize=12)
    style.map('TScrollbar',
              background=[('active', colors['fg_secondary'])])

    style.configure('TOptionMenu', background=colors['surface'],
                     foreground=colors['fg'])
    style.map('TOptionMenu',
              background=[('active', colors['border'])])


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
        label = tk.Label(
            tw, text=self.text, background="#333333", foreground="white",
            font=("Segoe UI", 9), padx=10, pady=5, relief="flat",
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
            padx=8,
            pady=8,
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
# TOGGLE SWITCH — Widget iOS-style
# ==========================================
class ToggleSwitch(tk.Canvas):
    def __init__(self, master, variable=None, command=None,
                 on_color='#38a169', off_color='#a0aec0',
                 button_color='#ffffff', bg=None, width=50, height=26, aa_scale=3, **kwargs):
        if bg is None:
            bg = master.cget('bg') if hasattr(master, 'cget') else '#d9d9d9'
        super().__init__(master, width=width, height=height,
                         highlightthickness=0, borderwidth=0, bg=bg, **kwargs)
        self._aa = aa_scale
        self._tw = width
        self._th = height
        self._is_on = variable.get() if variable else False
        self._variable = variable
        self._command = command
        self._colors = {
            'on': on_color,
            'off': off_color,
            'knob': button_color,
        }
        self._photo = None

        self.bind("<Button-1>", self._toggle)
        self._draw()

    def _draw(self):
        s = self._aa
        sw, sh = self._tw * s, self._th * s
        pad = 3 * s
        track_h = sh - 2 * pad
        r = track_h // 2

        img = PIL.Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
        d = PIL.ImageDraw.Draw(img)

        track_color = self._colors['on'] if self._is_on else self._colors['off']

        left = [pad, pad, pad + track_h, sh - pad]
        right = [sw - pad - track_h, pad, sw - pad, sh - pad]
        mid = [pad + r, pad, sw - pad - r, sh - pad]

        d.pieslice(left, 90, 270, fill=track_color)
        d.pieslice(right, 270, 90, fill=track_color)
        d.rectangle(mid, fill=track_color)

        cx = (sw - pad - r) if self._is_on else (pad + r)
        kr = r - 2 * s
        knob_top = pad + 2 * s
        knob_bot = sh - pad - 2 * s
        d.ellipse([cx - kr, knob_top, cx + kr, knob_bot], fill=self._colors['knob'])

        img = img.resize((self._tw, self._th), PIL.Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        self._photo = tk.PhotoImage(data=buf.read())
        self.delete("all")
        self.create_image(0, 0, anchor="nw", image=self._photo)

    def _toggle(self, event=None):
        self._is_on = not self._is_on
        if self._variable:
            self._variable.set(self._is_on)
        if self._command:
            self._command()
        self._draw()

    def get(self):
        return self._is_on

    def set(self, value):
        self._is_on = bool(value)
        self._draw()

    def set_bg(self, color):
        self.configure(bg=color)


# ==========================================
# STATUSBAR
# ==========================================
class StatusBar(ttk.Frame):
    def __init__(self, container, colors):
        super().__init__(container, style='Surface.TFrame')
        self.colors = colors
        self._progress = 0

        self.canvas = tk.Canvas(self, height=6, highlightthickness=0,
                                bg=colors['surface'])
        self.canvas.pack(fill="x")

        self.label = ttk.Label(self, text="Listo", style='Status.TLabel',
                               anchor="w", padding=(8, 4))
        self.label.pack(fill="x")

        self._draw_bar()

    def _draw_bar(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        if w <= 1:
            w = 400
        fill_w = int(w * self._progress / 100)
        if fill_w > 0:
            self.canvas.create_rectangle(0, 0, fill_w, 6,
                                         fill=self.colors['primary'], outline="")

    def set_progress(self, value):
        self._progress = max(0, min(100, value))
        self._draw_bar()

    def set_message(self, msg, progress=None):
        self.label.config(text=msg)
        if progress is not None:
            self.set_progress(progress)

    def clear(self):
        self.label.config(text="Listo")
        self._progress = 0
        self._draw_bar()


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
# FUNCIONES DE CALCULO DE eDPS
# ==========================================
def get_effectiveness_mult(attack_type, defender_types):
    """Calcula el multiplicador de efectividad de tipo."""
    eff = TYPE_EFFECTIVENESS.get(attack_type)
    if not eff:
        return 1.0
    immune, resisted, super_eff = eff
    mult = 1.0
    for dtype in defender_types:
        if dtype in immune:
            mult *= 0.390625
        elif dtype in resisted:
            mult *= 0.625
        elif dtype in super_eff:
            mult *= 1.6
    return mult


def get_types_effectiveness(defender_types):
    """Retorna mapa de efectividad de todos los tipos contra un defensor."""
    result = {}
    for atype in POKEMON_TYPES:
        result[atype] = get_effectiveness_mult(atype, defender_types)
    return result


def get_stab(pokemon_types, move_type, move_name):
    """Retorna multiplicador STAB (1.2x si es tipo propio y no es Hidden Power)."""
    if move_type in pokemon_types and not move_name.startswith("Hidden Power"):
        return 1.2
    return 1.0


def calc_damage(atk, def_, power, modifiers):
    """Formula de dano de Pokemon Go."""
    return 0.5 * power * (atk / def_) * modifiers + 0.5


def process_duration(duration_ms):
    """Redondea duracion al 0.5s mas cercano (modo pve_turns)."""
    return round((duration_ms / 1000) * 2) / 2


def process_power(move_obj):
    """Ajusta poder si la redondeo de duracion cambio significativamente."""
    new_dur = process_duration(move_obj["duration"])
    old_dur = move_obj["duration"] / 1000.0
    if new_dur > 0:
        modifier = (new_dur - old_dur) / new_dur
        if abs(modifier) >= 0.199:
            return move_obj["power"] * (1 + modifier)
    return move_obj["power"]


def get_pokemon_stats(pkm_obj, level=40, ivs=None):
    """Obtiene stats a un nivel especifico con IVs."""
    if ivs is None:
        ivs = {"atk": 15, "def": 15, "hp": 15}
    stats = pkm_obj.get("stats", {})
    cpm = CPM_LEVEL_40 if level == 40 else CPM_LEVEL_50
    atk = (stats.get("baseAttack", 0) + ivs["atk"]) * cpm
    def_ = (stats.get("baseDefense", 0) + ivs["def"]) * cpm
    hp = (stats.get("baseStamina", 0) + ivs["hp"]) * cpm
    return atk, def_, hp


def get_dps(types, atk, def_, hp, fm_obj, cm_obj, fm_mult=1, cm_mult=1,
            enemy_def=180, enemy_y=None):
    """Calcula DPS completo con ciclo de energia (mismo algoritmo que DialgaDex GetDPS)."""
    if not fm_obj or not cm_obj:
        return 0

    if enemy_y is None:
        enemy_y = {"y_num": None, "cm_num": None}

    y_num = enemy_y.get("y_num") or ESTIMATED_Y_NUMERATOR
    cm_num = enemy_y.get("cm_num") or ESTIMATED_CM_POWER

    y = y_num / def_ if def_ > 0 else ESTIMATED_Y_NUMERATOR / 180
    in_cm_dmg = cm_num / def_ if def_ > 0 else ESTIMATED_CM_POWER / 180

    fm_dur = process_duration(fm_obj["duration"])
    cm_dur = process_duration(cm_obj["duration"])

    if fm_dur <= 0 or cm_dur <= 0:
        return 0

    fm_power = process_power(fm_obj)
    cm_power = process_power(cm_obj)

    fm_stab = 1.2 if (fm_obj["type"] in types and fm_obj["name"] != "Hidden Power") else 1
    fm_dmg = calc_damage(atk, enemy_def, fm_power, fm_mult * fm_stab)
    fm_dps = fm_dmg / fm_dur
    fm_eps = fm_obj["energy_delta"] / fm_dur

    cm_stab = 1.2 if cm_obj["type"] in types else 1
    cm_dmg = calc_damage(atk, enemy_def, cm_power, cm_mult * cm_stab)
    cm_dps = cm_dmg / cm_dur

    if fm_dps > cm_dps:
        return fm_dps

    cm_eps = -cm_obj["energy_delta"] / cm_dur

    if cm_obj["energy_delta"] == -100:
        dws = 0
        cm_eps = (-cm_obj["energy_delta"] + 0.5 * fm_obj["energy_delta"]
                  + 0.5 * y * dws) / cm_dur

    x = 0.5 * (-cm_obj["energy_delta"]) + 0.5 * fm_obj["energy_delta"]
    x = x + 0.5 * in_cm_dmg

    tof = hp / y if y > 0 else hp

    f_to_c_ratio_num = (tof * (-cm_obj["energy_delta"]) + cm_dur * (x - 0.5 * hp))
    f_to_c_ratio_den = (tof * fm_obj["energy_delta"] - fm_dur * (x - 0.5 * hp))

    if f_to_c_ratio_den <= 0:
        return fm_dps

    f_to_c_ratio = f_to_c_ratio_num / f_to_c_ratio_den

    cm_dps_adj = cm_dps

    if cm_eps + fm_eps <= 0:
        return fm_dps

    dps0 = (fm_dps * cm_eps + cm_dps_adj * fm_eps) / (cm_eps + fm_eps)
    dps = dps0 + ((cm_dps_adj - fm_dps) / (cm_eps + fm_eps)) * (0.5 - x / hp) * y

    return fm_dps if fm_dps > dps else max(dps, 0)


def get_tdo(dps, hp, def_, enemy_y=None):
    """Calcula Total Damage Output."""
    if enemy_y is None:
        enemy_y = {"y_num": None}
    y_num = enemy_y.get("y_num") or ESTIMATED_Y_NUMERATOR
    y = y_num / def_ if def_ > 0 else ESTIMATED_Y_NUMERATOR / 180
    tof = hp / y if y > 0 else 1
    return dps * tof


def get_edps(dps, tdo, hp=1000000000, team_size=6, relobby_time=10):
    """Calcula eDPS efectivo con relobbying (mismo algoritmo que DialgaDex GetEDPS)."""
    if dps <= 0 or tdo <= 0:
        return 0
    RESPAWN_TIME = 1
    tof = tdo / dps
    lives = hp / tdo
    deaths = max(0, math.ceil(lives) - 1)
    relobbies = deaths // team_size
    ttw = lives * tof + (deaths - relobbies) * RESPAWN_TIME + relobby_time * relobbies
    return hp / ttw if ttw > 0 else 0


def get_specific_y(types, atk, fm_obj, cm_obj, total_incoming_dps=50):
    """Calcula el DPS del enemigo contra nuestro Pokemon."""
    if not fm_obj or not cm_obj:
        return {"Any": {"y_num": 0, "cm_num": 0}}

    CHARGED_MOVE_CHANCE = 0.3
    ENERGY_PER_HP = 0.5
    FM_DELAY = 1.75
    CM_DELAY = 0.5

    fm_stab = 1.2 if (fm_obj["type"] in types and fm_obj["name"] != "Hidden Power") else 1
    fm_power = process_power(fm_obj)
    fm_num = 0.5 * fm_power * fm_stab * atk
    fm_dur = process_duration(fm_obj["duration"]) + FM_DELAY

    cm_stab = 1.2 if cm_obj["type"] in types else 1
    cm_power = process_power(cm_obj)
    cm_num = 0.5 * cm_power * cm_stab * atk
    cm_dur = process_duration(cm_obj["duration"]) + CM_DELAY

    eps_for_damage = ENERGY_PER_HP * total_incoming_dps
    fms_per_cm = (-cm_obj["energy_delta"] - eps_for_damage * cm_dur) / \
                 (fm_obj["energy_delta"] + eps_for_damage * fm_dur)
    if fms_per_cm < 0:
        fms_per_cm = 0
    fms_per_cm = fms_per_cm + (1 / CHARGED_MOVE_CHANCE) - 1

    cycle_dur = fms_per_cm * fm_dur + cm_dur
    if cycle_dur <= 0:
        return {"Any": {"y_num": 0, "cm_num": 0}}

    type_ys = {"Any": {
        "y_num": (fms_per_cm * fm_num + cm_num) / cycle_dur,
        "cm_num": cm_num
    }}

    if fm_obj["type"] == cm_obj["type"]:
        type_ys[fm_obj["type"]] = type_ys["Any"]
    else:
        type_ys[fm_obj["type"]] = {
            "y_num": (fms_per_cm * fm_num) / cycle_dur,
            "cm_num": 0
        }
        type_ys[cm_obj["type"]] = {
            "y_num": cm_num / cycle_dur,
            "cm_num": cm_num
        }

    return type_ys


def avg_y_against(enemy_y, effectiveness):
    """Aplica efectividad de tipo al enemy_y."""
    result = {"y_num": 0, "cm_num": 0}
    for t, vals in enemy_y.items():
        if t == "Any":
            continue
        mult = effectiveness.get(t, 1.0)
        result["y_num"] += vals["y_num"] * mult
        result["cm_num"] += vals["cm_num"] * mult
    return result


def get_raid_stats(pkm_obj, tier=None):
    """Obtiene stats de jefe de raid."""
    if tier is None:
        tier = pkm_obj.get("raid_tier", 5)
    if pkm_obj.get("form") in ("Mega", "MegaY", "MegaZ"):
        tier = 4
    if pkm_obj.get("class") and pkm_obj.get("form") == "Mega":
        tier = 6

    cpm = RAID_TIER_CPM.get(tier, 0.79)
    ivs_atk, ivs_def, ivs_hp = 15, 15, 15
    stats = pkm_obj.get("stats", {})
    atk = (stats.get("baseAttack", 0) + ivs_atk) * cpm
    def_ = (stats.get("baseDefense", 0) + ivs_def) * cpm
    hp = RAID_TIER_HP.get(tier, 15000)
    return atk, def_, hp


def get_raid_bosses(all_pokemon, has_type=None, weak_to_type=None):
    """Encuentra jefes de raid de tier 4+."""
    bosses = []
    for p in all_pokemon:
        if not p.get("raid_tier") or p["raid_tier"] < 4:
            continue
        if has_type and has_type not in p.get("types", []):
            continue
        if weak_to_type:
            eff = get_effectiveness_mult(weak_to_type, p.get("types", []))
            if eff <= 1.01:
                continue
        bosses.append(p)
    return bosses


def get_type_affinity(all_pokemon, attack_type):
    """Calcula Type Affinity: promedio de jefes de raid debiles a un tipo."""
    bosses = get_raid_bosses(all_pokemon, weak_to_type=attack_type)
    if not bosses:
        bosses = get_raid_bosses(all_pokemon)

    avg_ys = {"Any": {"y_num": 0, "cm_num": 0}}
    for t in POKEMON_TYPES:
        avg_ys[t] = {"y_num": 0, "cm_num": 0}

    avg_stats = {"atk": 0, "def": 0, "hp": 0}
    avg_weakness = {t: 0 for t in POKEMON_TYPES}

    for boss in bosses:
        boss_types = boss.get("types", [])

        boss_atk, boss_def, boss_hp = get_raid_stats(boss)

        boss_weakness = get_types_effectiveness(boss_types)
        for t in POKEMON_TYPES:
            avg_weakness[t] += boss_weakness.get(t, 1.0)

        boss_fms = boss.get("fm", [])
        boss_cms = boss.get("cm", [])
        boss_elite_fms = boss.get("elite_fm", [])
        boss_elite_cms = boss.get("elite_cm", [])
        all_boss_fms = boss_fms + boss_elite_fms
        all_boss_cms = boss_cms + boss_elite_cms

        win_dps = boss_hp / (300 if boss.get("raid_tier", 5) >= 4 else 180)

        boss_ys_list = []
        for bfm in all_boss_fms:
            for bcm in all_boss_cms:
                bfm_obj = FAST_MOVES_DATA.get(bfm)
                bcm_obj = CHARGED_MOVES_DATA.get(bcm)
                if bfm_obj and bcm_obj:
                    sy = get_specific_y(boss_types, boss_atk, bfm_obj, bcm_obj, win_dps)
                    boss_ys_list.append(sy)

        if not boss_ys_list:
            continue

        boss_avg_y = {"Any": {"y_num": 0, "cm_num": 0}}
        for t in POKEMON_TYPES:
            boss_avg_y[t] = {"y_num": 0, "cm_num": 0}

        for sy in boss_ys_list:
            for t, vals in sy.items():
                if t in boss_avg_y:
                    boss_avg_y[t]["y_num"] += vals["y_num"]
                    boss_avg_y[t]["cm_num"] += vals["cm_num"]

        n = len(boss_ys_list)
        for t in boss_avg_y:
            boss_avg_y[t]["y_num"] /= n
            boss_avg_y[t]["cm_num"] /= n

        for t in POKEMON_TYPES:
            avg_ys[t]["y_num"] += boss_avg_y[t]["y_num"]
            avg_ys[t]["cm_num"] += boss_avg_y[t]["cm_num"]
        avg_ys["Any"]["y_num"] += boss_avg_y["Any"]["y_num"]
        avg_ys["Any"]["cm_num"] += boss_avg_y["Any"]["cm_num"]

        avg_stats["atk"] += boss_atk
        avg_stats["def"] += boss_def
        avg_stats["hp"] += boss_hp

    n_bosses = len(bosses) if bosses else 1
    for t in avg_ys:
        avg_ys[t]["y_num"] /= n_bosses
        avg_ys[t]["cm_num"] /= n_bosses
    avg_stats["atk"] /= n_bosses
    avg_stats["def"] /= n_bosses
    avg_stats["hp"] /= n_bosses
    for t in avg_weakness:
        avg_weakness[t] /= n_bosses

    return {
        "enemy_ys": [avg_ys],
        "stats": avg_stats,
        "weakness": avg_weakness,
    }


FAST_MOVES_DATA = {}
CHARGED_MOVES_DATA = {}
ALL_POKEMON_DATA = []


# ==========================================
# API CACHE
# ==========================================
class ApiCache:
    def __init__(self):
        self._cache_especie = {}
        self._cache_dialgadex = None
        self._cache_gamemaster = None
        self._cache_rankings = {}
        self._cache_fast_moves = None
        self._cache_charged_moves = None
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

    def descargar_fast_moves(self):
        if self._cache_fast_moves is not None:
            return self._cache_fast_moves
        try:
            r = self._session.get(FAST_MOVES_URL, timeout=30)
            if r.status_code == 200:
                self._cache_fast_moves = {m["name"]: m for m in r.json()}
                return self._cache_fast_moves
        except Exception:
            pass
        return None

    def descargar_charged_moves(self):
        if self._cache_charged_moves is not None:
            return self._cache_charged_moves
        try:
            r = self._session.get(CHARGED_MOVES_URL, timeout=30)
            if r.status_code == 200:
                self._cache_charged_moves = {m["name"]: m for m in r.json()}
                return self._cache_charged_moves
        except Exception:
            pass
        return None

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
    def __init__(self, container, api_cache, idioma_var, status_bar, colors):
        super().__init__(container, style='TFrame')
        self.api = api_cache
        self.idioma_var = idioma_var
        self.status_bar = status_bar
        self.colors = colors
        self._cache_ids = None
        self._prefijo_liga = ""
        self._liga_actual = None
        self._build_ui()

    def _generar_prefijo_liga(self, liga, idioma):
        cp_cap = PVPOKE_CP_CAPS.get(liga, 1500)
        if cp_cap is not None:
            if idioma == "English":
                return f"cp-{cp_cap}&-1attack&3-defense&3-hp&"
            else:
                return f"PC-{cp_cap}&3-4puntos de salud&3-4defensa&0-1ataque&"
        else:
            if idioma == "English":
                return "4*,3*&"
            else:
                return "4*;3*&"

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        frame_filtros = ttk.LabelFrame(self, text=" Filtros (aditivos) ", padding=12)
        frame_filtros.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        frame_filtros.columnconfigure(0, weight=1)
        frame_filtros.columnconfigure(1, weight=1)
        frame_filtros.columnconfigure(2, weight=1)

        self.var_mt = tk.BooleanVar(value=True)
        self.var_oscuro = tk.BooleanVar(value=True)
        self.var_xl = tk.BooleanVar(value=True)

        # Filtro MT de Élite
        f_mt = ttk.Frame(frame_filtros)
        f_mt.grid(row=0, column=0, padx=8, pady=4, sticky="ew")
        lbl_mt = ttk.Label(f_mt, text="MT de Élite")
        lbl_mt.pack(anchor="center")
        self.toggle_mt = ToggleSwitch(
            f_mt, variable=self.var_mt, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_mt.pack(anchor="center", pady=(4, 0))
        self.tooltip_mt = ToolTip(lbl_mt, get_tooltip_text(self.var_mt, "Pokemon que requieren MT de Élite"))
        self.var_mt.trace_add("write", lambda *a: self.tooltip_mt.set_text(get_tooltip_text(self.var_mt, "Pokemon que requieren MT de Élite")))

        # Filtro Oscuro
        f_oscuro = ttk.Frame(frame_filtros)
        f_oscuro.grid(row=0, column=1, padx=8, pady=4, sticky="ew")
        lbl_oscuro = ttk.Label(f_oscuro, text="Oscuro")
        lbl_oscuro.pack(anchor="center")
        self.toggle_oscuro = ToggleSwitch(
            f_oscuro, variable=self.var_oscuro, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_oscuro.pack(anchor="center", pady=(4, 0))
        self.tooltip_oscuro = ToolTip(lbl_oscuro, get_tooltip_text(self.var_oscuro, "Pokemon Shadow"))
        self.var_oscuro.trace_add("write", lambda *a: self.tooltip_oscuro.set_text(get_tooltip_text(self.var_oscuro, "Pokemon Shadow")))

        # Filtro Caramelos XL
        f_xl = ttk.Frame(frame_filtros)
        f_xl.grid(row=0, column=2, padx=8, pady=4, sticky="ew")
        lbl_xl = ttk.Label(f_xl, text="Caramelos XL")
        lbl_xl.pack(anchor="center")
        self.toggle_xl = ToggleSwitch(
            f_xl, variable=self.var_xl, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_xl.pack(anchor="center", pady=(4, 0))
        self.tooltip_xl = ToolTip(lbl_xl, get_tooltip_text(self.var_xl, "Pokemon que necesitan XL para alcanzar el CP cap"))
        self.var_xl.trace_add("write", lambda *a: self.tooltip_xl.set_text(get_tooltip_text(self.var_xl, "Pokemon que necesitan XL para alcanzar el CP cap")))

        # Acciones: cantidad + botones de liga en una fila
        frame_accion = ttk.Frame(self)
        frame_accion.grid(row=1, column=0, pady=(4, 8))
        frame_accion.columnconfigure(0, weight=1)

        lbl_cantidad = ttk.Label(frame_accion, text="Pokemon a incluir:")
        lbl_cantidad.grid(row=0, column=0, sticky="e")

        self.txt_cantidad = ttk.Entry(frame_accion, width=6, justify="center")
        self.txt_cantidad.insert(0, "200")
        self.txt_cantidad.grid(row=0, column=1, padx=(4, 12))

        self.btn_great = ttk.Button(
            frame_accion, text="Great League", style='Great.TButton',
            command=lambda: self._on_league_btn("Great League")
        )
        self.btn_great.grid(row=0, column=2, padx=4)

        self.btn_ultra = ttk.Button(
            frame_accion, text="Ultra League", style='Ultra.TButton',
            command=lambda: self._on_league_btn("Ultra League")
        )
        self.btn_ultra.grid(row=0, column=3, padx=4)

        self.btn_master = ttk.Button(
            frame_accion, text="Master League", style='Master.TButton',
            command=lambda: self._on_league_btn("Master League")
        )
        self.btn_master.grid(row=0, column=4, padx=4)

        self.output = TextInput(self, height=8, font=("Consolas", 10), wrap=tk.CHAR)
        self.output.grid(row=3, column=0, padx=12, pady=(6, 2), sticky="nsew")
        self.output.set_state(tk.DISABLED)

        frame_acciones = ttk.Frame(self)
        frame_acciones.grid(row=4, column=0, pady=(6, 10))

        btn_copiar = ttk.Button(frame_acciones, text="Copiar al Portapapeles",
                                style='Success.TButton', command=self._copiar)
        btn_copiar.pack(side=tk.LEFT, padx=6)

        btn_limpiar = ttk.Button(frame_acciones, text="Limpiar",
                                 style='Surface.TButton', command=self._limpiar)
        btn_limpiar.pack(side=tk.LEFT, padx=6)

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

    def _on_league_btn(self, liga):
        btn = {"Great League": self.btn_great, "Ultra League": self.btn_ultra, "Master League": self.btn_master}[liga]
        if btn.cget("text") == "Cancelar":
            self._cancelled = True
        else:
            self._liga_actual = liga
            self._obtener_lista_pvp(liga)

    def _obtener_lista_pvp(self, liga):
        idioma = self.idioma_var.get()
        btn_activo = {"Great League": self.btn_great, "Ultra League": self.btn_ultra, "Master League": self.btn_master}[liga]
        self._cancelled = False
        btn_activo.config(text="Cancelar")
        for b in (self.btn_great, self.btn_ultra, self.btn_master):
            if b is not btn_activo:
                b.config(state=tk.DISABLED)
        self.status_bar.set_message(f"Descargando datos de {liga}...", 0)
        self.update()

        gamemaster = self.api.descargar_gamemaster()
        if not gamemaster or self._cancelled:
            self._restaurar_botones_pvp()
            self.status_bar.clear()
            return

        rankings = self.api.descargar_rankings(liga)
        if not rankings or self._cancelled:
            self._restaurar_botones_pvp()
            self.status_bar.clear()
            return

        mt_elite = self.var_mt.get()
        oscuro = self.var_oscuro.get()
        xl = self.var_xl.get()

        filtrados = self._filtrar_pvpoke(gamemaster, rankings, liga, mt_elite, oscuro, xl)

        if not filtrados or self._cancelled:
            self._restaurar_botones_pvp()
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
        self._cache_ids = set()

        self._prefijo_liga = self._generar_prefijo_liga(liga, idioma)

        self.status_bar.set_message(f"Procesando {total} Pokemon...", 0)

        for i, p in enumerate(top):
            if self._cancelled:
                break
            nombre = limpiar_nombre_especie(p["speciesName"])
            resultado = self._obtener_id_raw(nombre)
            if resultado:
                self._cache_ids.add(resultado)
            pct = 100 * (i + 1) // total
            self.status_bar.set_message(f"Procesando {i+1}/{total} ({pct}%)", pct)
            self.update()

        if self._cancelled:
            self._restaurar_botones_pvp()
            self.status_bar.set_message("Cancelado", 0)
        else:
            self._regenerar()
            self._restaurar_botones_pvp()
            self.status_bar.set_message(f"Completado: {total} Pokemon procesados", 100)

    def _restaurar_botones_pvp(self):
        self.btn_great.config(state=tk.NORMAL, text="Great League")
        self.btn_ultra.config(state=tk.NORMAL, text="Ultra League")
        self.btn_master.config(state=tk.NORMAL, text="Master League")

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
        if self._liga_actual and self._cache_ids is not None:
            idioma = self.idioma_var.get()
            self._prefijo_liga = self._generar_prefijo_liga(self._liga_actual, idioma)
        self._regenerar()

    def update_toggle_bgs(self, bg):
        for toggle in (self.toggle_mt, self.toggle_oscuro, self.toggle_xl):
            toggle.set_bg(bg)


# ==========================================
# PESTAÑA 2 — DIALGADEX
# ==========================================
class DialgadexTab(ttk.Frame):
    def __init__(self, container, api_cache, idioma_var, status_bar, colors):
        super().__init__(container, style='TFrame')
        self.api = api_cache
        self.idioma_var = idioma_var
        self.status_bar = status_bar
        self.colors = colors
        self._cache_ids = None
        self._type_affinity_cache = {}
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        frame_filtros = ttk.LabelFrame(self, text=" Filtros (aditivos) ", padding=12)
        frame_filtros.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        frame_filtros.columnconfigure(0, weight=1)
        frame_filtros.columnconfigure(1, weight=1)
        frame_filtros.rowconfigure(0, weight=1)
        frame_filtros.rowconfigure(1, weight=1)

        self.var_inedito = tk.BooleanVar(value=False)
        self.var_mega = tk.BooleanVar(value=False)
        self.var_oscuro = tk.BooleanVar(value=True)
        self.var_legendario = tk.BooleanVar(value=True)

        # Filtro Inédito
        f_inedito = ttk.Frame(frame_filtros)
        f_inedito.grid(row=0, column=0, padx=8, pady=4, sticky="ew")
        lbl_inedito = ttk.Label(f_inedito, text="Inedito")
        lbl_inedito.pack(anchor="center")
        self.toggle_inedito = ToggleSwitch(
            f_inedito, variable=self.var_inedito, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_inedito.pack(anchor="center", pady=(4, 0))
        self.tooltip_inedito = ToolTip(lbl_inedito, get_tooltip_text(self.var_inedito, "Pokemon no lanzados"))
        self.var_inedito.trace_add("write", lambda *a: self.tooltip_inedito.set_text(get_tooltip_text(self.var_inedito, "Pokemon no lanzados")))

        # Filtro Mega / Primigenio
        f_mega = ttk.Frame(frame_filtros)
        f_mega.grid(row=0, column=1, padx=8, pady=4, sticky="ew")
        lbl_mega = ttk.Label(f_mega, text="Mega / Primigenio")
        lbl_mega.pack(anchor="center")
        self.toggle_mega = ToggleSwitch(
            f_mega, variable=self.var_mega, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_mega.pack(anchor="center", pady=(4, 0))
        self.tooltip_mega = ToolTip(lbl_mega, get_tooltip_text(self.var_mega, "Pokemon Mega y Primigenio"))
        self.var_mega.trace_add("write", lambda *a: self.tooltip_mega.set_text(get_tooltip_text(self.var_mega, "Pokemon Mega y Primigenio")))

        # Filtro Oscuro
        f_oscuro = ttk.Frame(frame_filtros)
        f_oscuro.grid(row=1, column=0, padx=8, pady=4, sticky="ew")
        lbl_oscuro = ttk.Label(f_oscuro, text="Oscuro")
        lbl_oscuro.pack(anchor="center")
        self.toggle_oscuro = ToggleSwitch(
            f_oscuro, variable=self.var_oscuro, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_oscuro.pack(anchor="center", pady=(4, 0))
        self.tooltip_oscuro = ToolTip(lbl_oscuro, get_tooltip_text(self.var_oscuro, "todas las formas Shadow-eligibles"))
        self.var_oscuro.trace_add("write", lambda *a: self.tooltip_oscuro.set_text(get_tooltip_text(self.var_oscuro, "todas las formas Shadow-eligibles")))

        # Filtro Legendario
        f_legendario = ttk.Frame(frame_filtros)
        f_legendario.grid(row=1, column=1, padx=8, pady=4, sticky="ew")
        lbl_legendario = ttk.Label(f_legendario, text="Legendario")
        lbl_legendario.pack(anchor="center")
        self.toggle_legendario = ToggleSwitch(
            f_legendario, variable=self.var_legendario, bg=self.winfo_toplevel().cget('bg'),
            on_color=self.colors['toggle_on'], off_color=self.colors['toggle_off'],
            button_color=self.colors['toggle_knob']
        )
        self.toggle_legendario.pack(anchor="center", pady=(4, 0))
        self.tooltip_legendario = ToolTip(lbl_legendario, get_tooltip_text(self.var_legendario, "Legendary, Mythic y Ultra Beast"))
        self.var_legendario.trace_add("write", lambda *a: self.tooltip_legendario.set_text(get_tooltip_text(self.var_legendario, "Legendary, Mythic y Ultra Beast")))

        # Acciones: cantidad + botón obtener en una fila
        frame_accion = ttk.Frame(self)
        frame_accion.grid(row=1, column=0, pady=(4, 8))
        frame_accion.columnconfigure(0, weight=1)

        lbl_cantidad = ttk.Label(frame_accion, text="Pokemon a incluir:")
        lbl_cantidad.grid(row=0, column=0, sticky="e")

        self.txt_cantidad = ttk.Entry(frame_accion, width=6, justify="center")
        self.txt_cantidad.insert(0, "200")
        self.txt_cantidad.grid(row=0, column=1, padx=(4, 12))

        self.btn_obtener = ttk.Button(
            frame_accion, text="Obtener Lista", style='Success.TButton',
            command=self._obtener_lista_atacantes
        )
        self.btn_obtener.grid(row=0, column=2, padx=4)

        self.output = TextInput(self, height=8, font=("Consolas", 10), wrap=tk.CHAR)
        self.output.grid(row=3, column=0, padx=12, pady=(6, 2), sticky="nsew")
        self.output.set_state(tk.DISABLED)

        frame_acciones = ttk.Frame(self)
        frame_acciones.grid(row=4, column=0, pady=(6, 10))

        btn_copiar = ttk.Button(frame_acciones, text="Copiar al Portapapeles",
                                style='Success.TButton', command=self._copiar)
        btn_copiar.pack(side=tk.LEFT, padx=6)

        btn_limpiar = ttk.Button(frame_acciones, text="Limpiar",
                                 style='Surface.TButton', command=self._limpiar)
        btn_limpiar.pack(side=tk.LEFT, padx=6)

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

        global FAST_MOVES_DATA, CHARGED_MOVES_DATA, ALL_POKEMON_DATA
        if not FAST_MOVES_DATA:
            FAST_MOVES_DATA = self.api.descargar_fast_moves() or {}
        if not CHARGED_MOVES_DATA:
            CHARGED_MOVES_DATA = self.api.descargar_charged_moves() or {}
        ALL_POKEMON_DATA = datos

        if FAST_MOVES_DATA and CHARGED_MOVES_DATA:
            self._type_affinity_cache = {}
            for t in POKEMON_TYPES:
                self._type_affinity_cache[t] = get_type_affinity(datos, t)
            for p in resultado:
                p["_edps"] = self._calcular_edps_pokemon(p)
            resultado.sort(key=lambda x: x.get("_edps", 0), reverse=True)
        else:
            resultado.sort(key=lambda x: x.get("stats", {}).get("baseAttack", 0), reverse=True)

        return resultado

    def _calcular_edps_pokemon(self, pkm_obj):
        """Calcula el mejor eDPS de un Pokemon usando Type Affinity."""
        types = pkm_obj.get("types", [])
        is_shadow = pkm_obj.get("shadow", False)

        atk, def_, hp = get_pokemon_stats(pkm_obj, level=40)
        if is_shadow:
            atk *= 1.2
            def_ *= 0.8333333
        hp = int(hp)

        attacker_effectiveness = get_types_effectiveness(types)

        fms = pkm_obj.get("fm", [])
        elite_fms = pkm_obj.get("elite_fm", [])
        cms = pkm_obj.get("cm", [])
        elite_cms = pkm_obj.get("elite_cm", [])

        all_fms = fms + elite_fms
        all_cms = cms + elite_cms

        if not all_fms or not all_cms:
            return 0

        best_edps = 0
        for fm_name in all_fms:
            fm_obj = FAST_MOVES_DATA.get(fm_name)
            if not fm_obj:
                continue

            for cm_name in all_cms:
                cm_obj = CHARGED_MOVES_DATA.get(cm_name)
                if not cm_obj:
                    continue

                cm_type = cm_obj["type"]
                enemy_params = self._type_affinity_cache.get(cm_type)
                if not enemy_params:
                    enemy_params = self._type_affinity_cache.get("Any")
                if not enemy_params:
                    continue

                enemy_ys = enemy_params["enemy_ys"]
                enemy_def = enemy_params["stats"]["def"]
                enemy_hp = enemy_params["stats"]["hp"]
                enemy_weakness = enemy_params["weakness"]

                fm_mult = enemy_weakness.get(fm_obj["type"], 1.0)
                cm_mult = enemy_weakness.get(cm_type, 1.0)

                best_combo_edps = 0
                for ey in enemy_ys:
                    y = avg_y_against(ey, attacker_effectiveness)

                    dps = get_dps(types, atk, def_, hp, fm_obj, cm_obj,
                                 fm_mult, cm_mult, enemy_def, y)
                    tdo = get_tdo(dps, hp, def_, y)
                    edps = get_edps(dps, tdo, enemy_hp, 6, 10)

                    if edps > best_combo_edps:
                        best_combo_edps = edps

                if best_combo_edps > best_edps:
                    best_edps = best_combo_edps

        return best_edps

    def _generar_cadena(self, lista_pokemon, cantidad):
        self._cancelled = False
        self.btn_obtener.config(text="Cancelar")
        self.status_bar.set_message("Generando cadena de busqueda...", 0)
        self.update()

        top = lista_pokemon[:cantidad]
        total = len(top)
        self._cache_ids = set()

        for i, p in enumerate(top):
            if self._cancelled:
                break
            nombre = limpiar_nombre_especie(p["name"])
            es_shadow = p.get("shadow", False)

            id_base = self.api.buscar_anteevolucion(nombre)
            if not id_base:
                id_base = p["id"]

            self._cache_ids.add((int(id_base), es_shadow))

            pct = 100 * (i + 1) // total
            self.status_bar.set_message(f"Procesando {i+1}/{total} ({pct}%)", pct)
            self.update()

        if self._cancelled:
            self.btn_obtener.config(state=tk.NORMAL, text="Obtener Lista")
            self.status_bar.set_message("Cancelado", 0)
        else:
            self._regenerar()
            self.btn_obtener.config(state=tk.NORMAL, text="Obtener Lista")
            self.status_bar.set_message(f"Completado: {total} Pokemon procesados", 100)

    def _obtener_lista_atacantes(self):
        if self.btn_obtener.cget("text") == "Cancelar":
            self._cancelled = True
            self.btn_obtener.config(text="Obtener Lista")
            self.status_bar.set_message("Cancelado", 0)
            return

        self._cancelled = False
        self.btn_obtener.config(text="Cancelar")
        self.status_bar.set_message("Descargando datos de Pokemon...", 0)
        self.update()

        datos = self.api.descargar_dialgadex()
        if not datos or self._cancelled:
            self.btn_obtener.config(state=tk.NORMAL, text="Obtener Lista")
            self.status_bar.clear()
            return

        self.status_bar.set_message("Descargando datos de movimientos...", 30)
        self.update()

        global FAST_MOVES_DATA, CHARGED_MOVES_DATA
        if not FAST_MOVES_DATA:
            FAST_MOVES_DATA = self.api.descargar_fast_moves() or {}
        if not CHARGED_MOVES_DATA:
            CHARGED_MOVES_DATA = self.api.descargar_charged_moves() or {}

        if not FAST_MOVES_DATA or not CHARGED_MOVES_DATA:
            messagebox.showwarning("Aviso", "No se pudieron descargar los datos de movimientos.")
            self.btn_obtener.config(state=tk.NORMAL, text="Obtener Lista")
            self.status_bar.clear()
            return

        self.status_bar.set_message("Filtrando atacantes...", 50)
        self.update()

        inedito = self.var_inedito.get()
        mega = self.var_mega.get()
        oscuro = self.var_oscuro.get()
        legendario = self.var_legendario.get()

        if not (inedito or mega or oscuro or legendario):
            messagebox.showwarning("Aviso", "Activa al menos un filtro.")
            self.btn_obtener.config(state=tk.NORMAL, text="Obtener Lista")
            self.status_bar.clear()
            return

        filtrados = self._filtrar_atacantes(datos, inedito, mega, oscuro, legendario)

        if not filtrados or self._cancelled:
            self.btn_obtener.config(state=tk.NORMAL, text="Obtener Lista")
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

    def update_toggle_bgs(self, bg):
        for toggle in (self.toggle_inedito, self.toggle_mega, self.toggle_oscuro, self.toggle_legendario):
            toggle.set_bg(bg)


# ==========================================
# VENTANA PRINCIPAL
# ==========================================
class PokeChainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PokeChain")
        self.geometry("620x870")
        self.minsize(540, 720)

        self.style = ttk.Style()
        self.dark_mode = False
        self.idioma = tk.StringVar(value="Español")

        self.api_cache = ApiCache()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        _icono = os.path.join(BASE_DIR, "icono.png")
        self._icon_img = None
        if os.path.exists(_icono):
            try:
                self._icon_img = tk.PhotoImage(file=_icono)
                self.iconphoto(True, self._icon_img)
            except tk.TclError:
                pass

        apply_theme(self.style, LIGHT_COLORS)
        self.configure(bg=LIGHT_COLORS['bg'])
        self.current_colors = LIGHT_COLORS

        self._create_menu()
        self._create_header()
        self._create_status_bar()
        self._create_notebook()

        self._bind_shortcuts()
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
        frame_top.pack(fill=tk.X, padx=12, pady=(10, 0))

        lbl_idioma = ttk.Label(frame_top, text="Idioma:")
        lbl_idioma.pack(side=tk.LEFT)

        menu_idioma = ttk.OptionMenu(frame_top, self.idioma, "Español", "Español", "English")
        menu_idioma.pack(side=tk.LEFT, padx=6)

        btn_tema = ttk.Button(frame_top, text="Cambiar tema",
                              style='Surface.TButton', command=self._toggle_theme)
        btn_tema.pack(side=tk.RIGHT)

    def _create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tab1 = PvPokeTab(self.notebook, self.api_cache, self.idioma, self._status_bar, self.current_colors)
        self.tab2 = DialgadexTab(self.notebook, self.api_cache, self.idioma, self._status_bar, self.current_colors)

        self.notebook.add(self.tab1, text="  PvPoke  ")
        self.notebook.add(self.tab2, text="  Dialgadex  ")

    def _create_status_bar(self):
        self._status_bar = StatusBar(self, self.current_colors)
        self._status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _bind_shortcuts(self):
        self.bind_all("<Control-Key-1>", lambda e: self.notebook.select(0))
        self.bind_all("<Control-Key-2>", lambda e: self.notebook.select(1))
        self.bind("<Control-t>", lambda e: self._toggle_theme())
        self.bind("<Control-q>", lambda e: self.destroy())

    def _toggle_theme(self):
        if self.dark_mode:
            apply_theme(self.style, LIGHT_COLORS)
            self.configure(bg=LIGHT_COLORS['bg'])
            self.current_colors = LIGHT_COLORS
            new_bg = LIGHT_COLORS['bg']
        else:
            apply_theme(self.style, DARK_COLORS)
            self.configure(bg=DARK_COLORS['bg'])
            self.current_colors = DARK_COLORS
            new_bg = DARK_COLORS['bg']
        self.dark_mode = not self.dark_mode
        self.tab1.update_toggle_bgs(new_bg)
        self.tab2.update_toggle_bgs(new_bg)
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
