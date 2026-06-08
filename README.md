# 🔍 Buscador de Anteevoluciones Pokémon

Herramienta de escritorio con interfaz gráfica (GUI) que convierte una lista de nombres de Pokémon en una cadena de IDs de sus anteevoluciones base, lista para usar en aplicaciones externas (como Pokémon GO o similares).

---

## ¿Qué hace?

Dado un listado de nombres de Pokémon (uno por línea), la herramienta:

1. Detecta si el Pokémon es de tipo **Shadow / Oscuro**.
2. Consulta la [PokéAPI](https://pokeapi.co/) para recorrer la cadena evolutiva hacia atrás hasta encontrar la forma base.
3. Devuelve los IDs de todas las formas base, sin duplicados, ordenados numéricamente y formateados como cadena separada por punto y coma.

**Ejemplo de salida:**
```
+1;+4;+7;Shadow&+150;
```

---

## Instalación en Windows

### 1. Instalar Python

Descarga Python desde [python.org](https://www.python.org/downloads/). Durante la instalación, **marca la casilla "Add Python to PATH"** antes de pulsar Install.

> `tkinter` viene incluido en la instalación estándar de Python para Windows, no requiere ningún paso adicional.

### 2. Instalar dependencias

Abre el símbolo del sistema (`cmd`) y ejecuta:

```cmd
pip install requests
```

### 3. Ejecutar

```cmd
python buscador_anteevoluciones.py
```

O haz **doble clic** sobre el archivo `.py` si Python está asociado como predeterminado.

---

## Instalación en Linux

### 1. Instalar Python

Python 3 suele venir preinstalado. Puedes verificarlo con:

```bash
python3 --version
```

Si no está disponible, instálalo con el gestor de paquetes de tu distro:

```bash
# Ubuntu / Debian
sudo apt install python3

# Fedora
sudo dnf install python3

# Arch
sudo pacman -S python
```

### 2. Instalar dependencias

A diferencia de Windows, `tkinter` no siempre viene incluido con Python en Linux y debe instalarse por separado:

```bash
# Ubuntu / Debian
sudo apt install python3-tk python3-pip
pip3 install requests

# Fedora
sudo dnf install python3-tkinter
pip3 install requests

# Arch
sudo pacman -S tk
pip install requests
```

### 3. Ejecutar

```bash
python3 buscador_anteevoluciones.py
```

---

## Uso

1. Pega tu lista de Pokémon en el campo de texto superior (un Pokémon por línea).
2. Pulsa **Convertir Lista**.
3. Espera a que se procesen las consultas a la API (puede tardar varios segundos según el tamaño de la lista).
4. Copia el resultado con el botón **Copiar al Portapapeles**.

---

## Formato de entrada admitido

| Entrada | Comportamiento |
|---|---|
| `Mewtwo` | Busca la forma base de Mewtwo |
| `Mewtwo (Shadow)` | Lo marca como Shadow en la salida |
| `Mewtwo (Oscuro)` | Equivalente a Shadow (variante en español) |
| `Charizard` | Devuelve el ID de Charmander (forma base) |

---

## Formato de salida

- Los IDs van precedidos de `+` (e.g., `+1`).
- Los Pokémon Shadow llevan el prefijo `Shadow&` (e.g., `Shadow&+150`).
- Los Pokémon Oscuros llevan el prefijo `Oscuro&` (e.g., `Oscuro&+150`).
- Los resultados están deduplicados y ordenados numéricamente por ID.
- La cadena termina siempre en `;`.

---

## Estructura del código

```
buscador_anteevoluciones.py
│
├── analizar_nombre()       # Extrae el prefijo Shadow/Oscuro y limpia el nombre
├── obtener_anteevolucion_id()  # Llama a PokéAPI y recorre la cadena evolutiva
├── criterio_ordenacion()   # Función de orden numérico para el ID
├── procesar_lista()        # Lógica principal al pulsar el botón
├── copiar_al_portapapeles()    # Copia el resultado al clipboard
└── GUI (tkinter)           # Definición de la ventana y sus componentes
```

---

## Notas

- La herramienta hace una petición HTTP a PokéAPI por cada Pokémon. Con listas largas, el procesamiento puede tomar tiempo.
- Si un Pokémon no se encuentra en la API, simplemente se omite sin mostrar error.
- Los nombres de entrada no distinguen mayúsculas de minúsculas.

---

## Dependencias externas

| Dependencia | Uso |
|---|---|
| [PokéAPI](https://pokeapi.co/) | Obtener datos de especie y cadena evolutiva |
| `requests` | Realizar las peticiones HTTP |
| `tkinter` | Interfaz gráfica de escritorio |