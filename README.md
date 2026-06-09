Aquí tienes el archivo `README.md` completamente actualizado para reflejar todas las nuevas funciones, la división por pestañas, el procesamiento avanzado de cadenas y la integración de la API en ambas herramientas.

---

# 🔍 PokeChain

**PokeChain** es una herramienta de escritorio con interfaz gráfica (GUI) diseñada para automatizar, limpiar y optimizar cadenas de búsqueda de Pokémon. Utiliza la [PokéAPI](https://pokeapi.co/) para rastrear líneas evolutivas y consolidar filtros avanzados compatibles con juegos y bases de datos externas.

---

## 🚀 Características Principales

La aplicación se divide en dos módulos especializados accesibles mediante pestañas:

### 1. Buscador de Anteevoluciones (Pestaña 1)

Convierte un listado de nombres de Pokémon en una cadena optimizada de IDs de sus formas base.

* **Rastreo Evolutivo:** Consulta la API en tiempo real para encontrar la preevolución inicial de cualquier Pokémon introducido.
* **Detección de Estado:** Identifica automáticamente si el Pokémon es *Shadow* u *Oscuro* y le añade el prefijo correspondiente.
* **Filtros de Liga Ajustables:** Permite añadir instantáneamente prefijos de filtrado de estadísticas para ligas específicas (*Great League* y *Ultra League*) con un solo clic.

### 2. Dialgadex Helper (Pestaña 2)

Parsea, sanea y traduce cadenas de búsqueda complejas ya existentes, aplicando también el filtro de anteevoluciones a los IDs numéricos.

* **Limpieza de Modificadores Mega:** Remueve de forma inteligente etiquetas como `mega`, `mega1-` o residuos de conectores `&`.
* **Filtro de Exclusión:** Descarta por completo bloques que contengan la palabra `investigación` y elimina términos huérfanos sueltos (como palabras `Oscuro` o `Shadow` sin ID asociado).
* **Traducción Dinámica:** Traduce automáticamente todos los tipos elementales (ej: *Fuego* ↔ *Fire*) y estados según el idioma seleccionado en la interfaz.
* **Conversión de IDs Existentes:** Toma los IDs numéricos o combinados de la cadena (ej: `26` o `Oscuro&26`) y los reemplaza por el ID de su anteevolución base (`+172` o `Oscuro&+172`), ordenando numéricamente todo el conjunto final.
* **Prefijo Automatizado:** Añade al inicio de la cadena resultante el filtro de calidad predeterminado (`4*;3*;3-ataque&!#&`).

---

## 🛠️ Instalación

### Windows

1. **Instalar Python:** Descárgalo desde [python.org](https://www.python.org/downloads/). Durante la instalación, asegúrate de marcar la casilla **"Add Python to PATH"**.
2. **Instalar Dependencias:** Abre la terminal (`cmd`) y ejecuta:
```cmd
pip install requests

```


3. **Ejecutar:** Haz doble clic sobre el archivo `pokechain.py` o ejecútalo desde la terminal:
```cmd
python pokechain.py

```



### Linux (Ubuntu / Debian / Fedora / Arch)

1. **Instalar Python y Tkinter:**
```bash
# Ubuntu / Debian
sudo apt install python3 python3-tk python3-pip

# Fedora
sudo dnf install python3 python3-tkinter

# Arch
sudo pacman -S python tk

```


2. **Instalar Dependencias:**
```bash
pip3 install requests

```


3. **Ejecutar:**
```bash
python3 pokechain.py

```



---

## 📊 Formatos de Entrada y Transformaciones

### Módulo 1 (Búsqueda por nombres)

| Entrada (Línea por línea) | Resultado Producido | Nota |
| --- | --- | --- |
| `Charizard` | `+4;` | Encuentra a Charmander (ID 4) |
| `Mewtwo (Shadow)` | `Shadow&+150;` | Mantiene el estado en inglés |
| `Mewtwo (Oscuro)` | `Oscuro&+150;` | Mantiene el estado en español |

### Módulo 2 (Dialgadex Helper - Cadena Completa)

| Cadena de Entrada de Ejemplo | Salida Procesada (Idioma: Español) |
| --- | --- |
| `mega2-&fuego,investigación;26;Oscuro&643` | `4*;3*;3-ataque&!#&Fuego;+172;Oscuro&+643;` |

*El sistema elimina los residuos "mega", descarta el bloque de "investigación", traduce "fuego" a formato correcto, y convierte el ID `26` (Raichu) en `+172` (Pichu).*

---

## 🗂️ Estructura del Código

```
pokechain.py
│
├── Lógica Compartida
│   ├── obtener_id_anteevolucion_puro() # Conexión iterativa con PokéAPI
│   └── criterio_ordenacion()          # Extractor de secuencias numéricas para ordenación
│
├── Módulo Pestaña 1
│   ├── analizar_nombre()              # Separa texto limpio de modificadores
│   ├── obtener_anteevolucion_id()     # Genera el token final formateado
│   └── aplicar_liga()                 # Inserción de cadenas de filtrado estático
│
└── Módulo Pestaña 2
    ├── parsear_cadena_existente()     # Limpieza, traducción y conversión de IDs
    └── procesar_concatenar()          # Formateo final con cabecera fija

```

---

## 📝 Notas de Uso

* **Consumo de API:** Las consultas se realizan bajo demanda a los servidores de PokéAPI. Al procesar listas muy extensas o cadenas con decenas de IDs, el programa puede tardar unos segundos en responder mientras asegura los datos de origen.
* **Persistencia del Idioma:** Cambiar el selector de idioma en cualquiera de las dos pestañas actualiza de forma global las preferencias de traducción y nomenclatura para todo el entorno de trabajo.