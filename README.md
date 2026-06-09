# PokeChain

Generador de cadenas de busqueda de Pokemon para Pokemon Go. Auto-descarga rankings de PvPoke y datos de DialgaDex, aplica filtros y genera listas listas para copiar y pegar.

---

## Instalacion en Windows (equipo recien formateado)

### Paso 1: Instalar Python

1. Ve a https://www.python.org/downloads/
2. Haz clic en **Download Python 3.x.x** (el boton grande amarillo)
3. Ejecuta el instalador descargado
4. **IMPORTANTE:** Marca la casilla **"Add python.exe to PATH"** antes de instalar
5. Haz clic en **Install Now**
6. Espera a que termine y haz clic en **Close**

### Paso 2: Verificar la instalacion

Abre **PowerShell** (haz clic derecho en el boton de Windows y selecciona "Terminal" o "PowerShell") y escribe:

```
python --version
```

Si ves algo como `Python 3.12.x`, todo esta bien. Si da error, cierra y vuelve a abrir la terminal.

### Paso 3: Descargar el programa

1. Descarga o clona este repositorio en cualquier carpeta (por ejemplo `C:\PokeChain`)
2. Abre PowerShell en esa carpeta:
   - Haz clic derecho dentro de la carpeta y selecciona **"Abrir en Terminal"** o **"Open in Terminal"**
   - O bien, escribe `cd C:\PokeChain` en PowerShell

### Paso 4: Instalar dependencias

En la terminal, escribe:

```
pip install requests Pillow
```

### Paso 5: Ejecutar

En la terminal, escribe:

```
python pokechain.py
```

---

## Instalacion en Linux (equipo recien formateado)

### Paso 1: Instalar Python y dependencias del sistema

**Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-tk python3-pil python3-pil.imagetk
```

**Fedora:**

```bash
sudo dnf install -y python3 python3-pip python3-tkinter python3-pillow-tk
```

**Arch / Manjaro:**

```bash
sudo pacman -S python python-pip tk pillow
```

### Paso 2: Verificar la instalacion

```bash
python3 --version
```

Si ves `Python 3.x.x`, esta todo correcto.

### Paso 3: Descargar el programa

```bash
git clone https://github.com/USUARIO/PokeChain.git
cd PokeChain
```

O simplemente descarga el archivo `pokechain.py` y colocalo en una carpeta.

### Paso 4: Instalar dependencias de Python

```bash
pip3 install requests Pillow
```

### Paso 5: Ejecutar

```bash
python3 pokechain.py
```

---

## Uso

### Pestana PvPoke

1. Selecciona los filtros que quieras (MT de Elite, Oscuro, Caramelos XL)
2. Indica cuantos Pokemon quieres incluir
3. Haz clic en **Great League**, **Ultra League** o **Master League**
4. Espera a que se descarguen y procesen los datos
5. Haz clic en **Copiar al Portapapeles**
6. Pegalo en Pokemon Go

### Pestana Dialgadex

1. Selecciona los filtros (Inedito, Mega/Primigenio, Oscuro, Legendario)
2. Indica cuantos Pokemon quieres incluir
3. Haz clic en **Obtener Lista**
4. Espera a que se descarguen y procesen los datos
5. Haz clic en **Copiar al Portapapeles**
6. Pegalo en Pokemon Go

### Otras funciones

- **Cambiar tema:** Pulsa `Ctrl+T` o usa el menu "Ver" para alternar entre modo claro y oscuro
- **Cambiar idioma:** Usa el selector de idioma en la esquina superior derecha
- **Cancelar proceso:** Haz clic en el boton que esta en proceso (cambia a "Cancelar") para detenerlo
- **Limpiar salida:** Haz clic en "Limpiar" para borrar el texto generado

---

## Atajos de teclado

| Atajo | Accion |
|-------|--------|
| `Ctrl+1` | Cambiar a pestana PvPoke |
| `Ctrl+2` | Cambiar a pestana Dialgadex |
| `Ctrl+T` | Cambiar tema (claro/oscuro) |
| `Ctrl+Q` | Cerrar programa |

---

## Requisitos

- Python 3.8 o superior
- tkinter (incluido con Python en Windows, en Linux hay que instalarlo aparte)
- Pillow (PIL)
- requests
- Conexion a internet para descargar datos de PvPoke y DialgaDex
