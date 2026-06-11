# ACCESS-A-WEB

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_App-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Base_de_datos-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-Editor-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![License](https://img.shields.io/badge/Llicència-GPLv3-blue?style=for-the-badge)

> Herramienta para transformar y visualizar vía web archivos **Microsoft Access** (`.accdb` / `.mdb`) que han quedado fuera de los sistemas informáticos actuales, convirtiéndolos en aplicaciones web ligeras con **Flask** y **SQLite**.

---

## 📋 Tabla de contenidos

- [ACCESS-A-WEB](#access-a-web)
  - [📋 Tabla de contenidos](#-tabla-de-contenidos)
  - [📖 Descripción](#-descripción)
  - [🔧 Requisitos previos](#-requisitos-previos)
  - [🚀 Instalación](#-instalación)
  - [▶️ Uso](#️-uso)
  - [⚙️ Parámetros de configuración](#️-parámetros-de-configuración)
  - [🌐 Desplegar la aplicación](#-desplegar-la-aplicación)
    - [🔄 Modificar la estructura de la base de datos SQLite](#-modificar-la-estructura-de-la-base-de-datos-sqlite)
  - [📝 Nota importante](#-nota-importante)

---

## 📖 Descripción

**ACCESS-A-WEB** permite dar una segunda vida a los archivos Access olvidados de las organizaciones. A partir de un fichero `.accdb` o `.mdb`, genera automáticamente:

- Una base de datos **SQLite** equivalente.
- Una **aplicación web Flask** completa para consultar y visualizar los datos.
- Una herramienta de consultas SQL para el usuario administrador, orientada a pequeñas modificaciones en serie.

> ℹ️ **Nota:** El objetivo de esta herramienta **no es** ser una solución completa de gestión de bases de datos, sino facilitar la recuperación y visualización de datos Access dentro de entornos web modernos. Únicamente pretende ahorarse la adquisición de licencias de MS Office que incluyan ACCESS.

---

## 🔧 Requisitos previos

| Herramienta | Descripción |
|---|---|
| [Python 3.x](https://www.python.org/downloads/) | Intérprete de Python |
| [Visual Studio Code](https://code.visualstudio.com/download) | Editor de código recomendado |
| Extensión **Jupyter** para VS Code | Necesaria para ejecutar el notebook |

---

## 🚀 Instalación

**1. Descarga y descomprime el proyecto**

Guarda la carpeta `ACCESS-A-WEB` en el directorio que prefieras.

**2. Prepara los archivos de entrada**

Coloca en la raíz de la carpeta `ACCESS-A-WEB`:
- Tu archivo Access (`.accdb` o `.mdb`).
- Tu logotipo en formato `JPG` o `PNG` *(opcional)*.

**3. Instala la extensión Jupyter en VS Code**

Abre VS Code e instala la extensión **Jupyter** desde:
- Menú `View > Extensions`, o
- Combinación de teclas `Ctrl+Shift+X`.

**4. Abre el proyecto en VS Code**

```
File > Open Folder > [selecciona la carpeta ACCESS-A-WEB]
```

**5. Abre un terminal integrado**

```
Terminal > New Terminal   (o Ctrl+Shift+ñ)
```

**6. Crea un entorno virtual**

```bash
python -m venv .venv
```

**7. Activa el entorno virtual**

```powershell
.venv\Scripts\Activate.ps1
```

**8. Instala las dependencias**

```bash
pip install -r requirements.txt
```

---

## ▶️ Uso

**1. Abre el notebook `ACCESS-A-WEB.ipynb`**

**2. Configura los parámetros de la primera celda** *(véase la sección [Parámetros de configuración](#️-parámetros-de-configuración))*

**3. Ejecuta todas las celdas**

Haz clic en el botón **RUN ALL** y, cuando se solicite el kernel, selecciona:

1. `PYTHON ENVIRONMENTS`
2. `.VENV`

> ⚠️ **Aviso:** La ejecución puede tardar bastante tiempo. Si se detiene, puedes interrumpir el kernel y volver a ejecutarlo.

**4. Sigue las instrucciones de la última celda**

Una vez finalizada la ejecución, la última celda del notebook indicará los pasos para poner en marcha la aplicación web generada.

---

## ⚙️ Parámetros de configuración

Modifica estos valores en la **primera celda** del notebook `ACCESS-A-WEB.ipynb`:

| Parámetro | Valor por defecto | Descripción |
|---|---|---|
| `INPUT_ACCDB` | `"Northwind.accdb"` | Archivo Access de entrada (`.accdb` o `.mdb`) |
| `OUTPUT_SQLITE` | `"Northwind.sqlite"` | Nombre del archivo SQLite de salida |
| `FLASK_OUTPUT_DIR` | `"app_web"` | Carpeta donde se generará la aplicación web |
| `APP_TITLE` | `"Gestor de Base de dades"` | Título que aparecerá en la aplicación web |
| `LOGO_PATH` | `"logo.png"` | Logotipo que se mostrará dentro de la app web |

**Ejemplo:**

```python
INPUT_ACCDB      = "ElMeuArxiu.accdb"
OUTPUT_SQLITE    = "ElMeuArxiu.sqlite"
FLASK_OUTPUT_DIR = "la_meva_app"
APP_TITLE        = "Arxiu Municipal"
LOGO_PATH        = "logo_ajuntament.png"
```

---

## 🌐 Desplegar la aplicación

Una vez generada la aplicación en la carpeta indicada en `FLASK_OUTPUT_DIR`, es necesario colocarla y configurarla en un **servidor web** para acceder a ella de forma habitual.

### 🔄 Modificar la estructura de la base de datos SQLite

Si es necesario modificar tablas o la estructura de la base de datos generada mediante la herramienta de consultas SQL del administrador, sigue este procedimiento:

1. Realiza los cambios necesarios en el archivo SQLite de la app web.
2. Haz una **copia de seguridad** del archivo SQLite, preferentemente fuera de la carpeta `ACCESS-A-WEB`.
3. Pega una copia del archivo SQLite dentro de la carpeta `ACCESS-A-WEB` (junto con el logo). **No es necesario ningún fichero `.accdb` o `.mdb`.**
4. Elimina la carpeta de la app web actual.
5. Vuelve a ejecutar `ACCESS-A-WEB.ipynb` **celda a celda**, **sin ejecutar la celda 4** (la que procesa el archivo Access original).

---

## 📝 Nota importante

Esta herramienta **no pretende sustituir** soluciones profesionales de gestión de bases de datos. Para tareas complejas de administración, existen diversas opciones de software libre disponibles en la red.

La herramienta de consultas SQL del administrador está pensada únicamente para facilitar **pequeñas modificaciones en serie** sobre los datos.

---
