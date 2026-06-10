# PokeChain

Herramienta de escritorio con GUI para generar cadenas de búsqueda optimizadas de Pokémon, usando rankings reales de PvPoke y DialgaDex.

---

## Características

La app tiene dos módulos en pestañas separadas:

### 1. PvPoke Tab (PvP)

Descarga rankings de PvPoke para **Great League**, **Ultra League** y **Master League**, los filtra y genera una cadena de búsqueda optimizada con IDs de formas base.

- Rankings desde la API oficial de PvPoke
- Filtros: oscuros, movimientos élite, XL
- Prefijos de filtrado por CP y estadísticas según la liga
- Resolución de anteevoluciones vía PokéAPI (recorre `evolves_from_species`)

### 2. DialgaDex Tab (Atacantes)

Scrapea rankings de atacantes desde [dialgadex.com](https://dialgadex.com) usando **Playwright**, los filtra según filtros del usuario y genera una cadena de búsqueda.

- Scraping con Playwright (Chromium headless)
- Filtros aditivos: Inédito, Oscuro, Mega/Primal, Legendario
- Resolución de anteevoluciones vía PokéAPI (recorre `evolves_from_species`)
- Datos crudos de [pogo_pkm.min.json](https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_pkm.min.json) para determinar si un Pokémon está liberado

---

## Instalación

### Windows

1. **Instalar Python 3** desde [python.org](https://www.python.org/downloads/). Marca **"Add Python to PATH"**.
2. **Instalar dependencias:**
   ```cmd
   pip install requests plyer
   pip install playwright
   python -m playwright install chromium
   ```
3. **Ejecutar:**
   ```cmd
   python pokechain.py
   ```

### Linux (Ubuntu / Debian / Fedora / Arch)

1. **Python y Tkinter:**
   ```bash
   # Ubuntu / Debian
   sudo apt install python3 python3-tk python3-pip

   # Fedora
   sudo dnf install python3 python3-tkinter

   # Arch
   sudo pacman -S python tk
   ```

2. **Dependencias:**
   ```bash
   pip3 install requests plyer
   pip3 install playwright
   python3 -m playwright install chromium
   ```

3. **Ejecutar:**
   ```bash
   python3 pokechain.py
   ```

---

## Uso

### PvPoke Tab
1. Seleccioná una liga (Great/Ultra/Master)
2. Activá los filtros deseados (oscuridad, MT élite, XL)
3. Ingresá la cantidad de Pokémon a incluir
4. Click en **Obtener Lista**
5. La cadena generada se copia al portapapeles

### DialgaDex Tab
1. Activá los filtros deseados (Inédito, Oscuro, Mega/Primal, Legendario)
2. Ingresá la cantidad de Pokémon a incluir
3. Click en **Obtener Lista** (abre Chromium headless, descarga rankings, aplica filtros)
4. La cadena generada se copia al portapapeles

---

## APIs y Fuentes de Datos

| Fuente | Uso | Endpoint |
|---|---|---|
| [dialgadex.com](https://dialgadex.com) | Rankings de atacantes (eDPS) | Scraping con Playwright |
| [PvPoke](https://pvpoke.com) | Rankings PvP por liga | `https://pvpoke.com/data/rankings/` |
| [PokéAPI](https://pokeapi.co) | Resolución de anteevoluciones | `https://pokeapi.co/api/v2/pokemon-species/` |
| [pokemon-resources](https://raw.githubusercontent.com/mgrann03/pokemon-resources/main/pogo_pkm.min.json) | Datos crudos de Pokémon GO (released, tipos) | GitHub raw |

---

## Estructura del Código

```
pokechain.py
├── Funciones compartidas
│   ├── limpiar_nombre_especie()   # Remueve prefijos Mega/Shadow y sufijos X/Y/Z
│   ├── analizar_nombre()          # Separa nombre de modificadores (Shadow/Oscuro)
│   ├── criterio_ordenacion()      # Ordena IDs numéricamente
│   └── get_prefijo_shadow()       # Prefijo según idioma
│
├── ApiCache
│   ├── consulta_api()             # GET con caché (PokéAPI)
│   ├── descargar_dialgadex()      # JSON de pokemon-resources
│   ├── descargar_gamemaster()     # GameMaster de PvPoke
│   ├── descargar_rankings()       # Rankings de PvPoke
│   └── buscar_anteevolucion()     # Recorre evolves_from_species
│
├── PvPokeTab
│   ├── _obtener_lista_pvp()       # Obtiene rankings PvP, filtra, genera cadena
│   ├── _filtrar_pvpoke()          # Filtra por oscuro, MT élite, XL
│   ├── _obtener_id_raw()          # Resuelve anteevolución + raw ID
│   └── _regenerar()               # Construye cadena de búsqueda final
│
├── DialgadexTab
│   ├── _get_browser()             # Lanza Chromium headless (Playwright)
│   ├── _scrape_rankings()         # Scrapea dialgadex.com, ejecuta LoadStrongest
│   ├── _filtrar_rankings()        # Filtra según toggles del usuario
│   ├── _generar_cadena()          # Resuelve anteevoluciones, genera cadena
│   └── _cleanup_playwright()      # Limpia recursos del navegador
│
└── PokeChainApp
    ├── _create_notebook()         # Pestañas PvP + DialgaDex
    ├── _create_header()           # Logo + selector de idioma
    ├── _create_menu()             # Menú Archivo + Tema
    └── _on_close()                # Cleanup de Playwright al cerrar
```

---

## Ejemplos

### PvPoke Tab — Great League

Entrada: top 10 de Great League con filtro oscuro activado

Salida: cadena con IDs base ordenados + prefijo `cp-1500&...`

### DialgaDex Tab — Atacantes generales

Entrada: top 5 con filtros Mega y Legendario activados

Proceso:
1. Playwright scrapea `dialgadex.com/?strongest&t=Any`
2. LoadStrongest calcula eDPS en el navegador
3. Se extraen 1676 Pokémon rankeados
4. Se filtran por Mega y Legendario
5. Cada Pokémon resuelve su anteevolución vía PokéAPI
6. Se genera cadena con IDs base

Ejemplo de resolución de anteevolución:
| Pokémon en ranking | ID ranking | Anteevolución | ID base |
|---|---|---|---|
| Charizard | 6 | Charmander | 4 |
| Gengar | 94 | Gastly | 92 |
| Salamence | 373 | Bagon | 371 |
| Mega Lucario | 448 | Riolu | 447 |

---

## Notas

- **Playwright:** En el primer uso descarga Chromium (~150 MB). Requiere conexión a internet.
- **dialgadex.com:** Los cálculos de eDPS se ejecutan en el navegador. La app espera hasta 60 segundos.
- **PokéAPI:** Las consultas de anteevolución se cachean en memoria durante la sesión.
- **Límite de velocidad:** PokéAPI tiene rate limit; para listas extensas puede tomar unos segundos.
