# ACCESS-A-WEB

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_App-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-Editor-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![License](https://img.shields.io/badge/Llicència-GPLv3-blue?style=for-the-badge)

> Tool to transform and visualise via web **Microsoft Access** files (`.accdb` / `.mdb`) that have been left out of current IT systems, converting them into lightweight web applications with **Flask** and **SQLite**.

---

## 📋 Table of contents

- [ACCESS-A-WEB](#access-a-web)
  - [📋 Table of contents](#-table-of-contents)
  - [📖 Description](#-description)
  - [🔧 Prerequisites](#-prerequisites)
  - [🚀 Installation](#-installation)
  - [▶️ Usage](#️-usage)
  - [⚙️ Configuration parameters](#️-configuration-parameters)
  - [🌐 Deploying the application](#-deploying-the-application)
    - [🔄 Modifying the SQLite database structure](#-modifying-the-sqlite-database-structure)
  - [📝 Important note](#-important-note)

---

## 📖 Description

**ACCESS-A-WEB** gives a second life to forgotten Access files in organisations. From an `.accdb` or `.mdb` file, it automatically generates:

- An equivalent **SQLite** database.
- A complete **Flask web application** to query and visualise the data.
- A SQL query tool for the administrator user, aimed at small batch modifications.

> ℹ️ **Note:** The purpose of this tool is **not** to be a complete database management solution, but to facilitate the recovery and visualisation of Access data within modern web environments. Its sole purpose is to avoid the cost of purchasing MS Office licenses that include ACCESS.

---

## 🔧 Prerequisites

| Tool | Description |
|---|---|
| [Python 3.x](https://www.python.org/downloads/) | Python interpreter |
| [Visual Studio Code](https://code.visualstudio.com/download) | Recommended code editor |
| **Jupyter** extension for VS Code | Required to run the notebook |

---

## 🚀 Installation

**1. Download and extract the project**

Save the `ACCESS-A-WEB` folder to the directory of your choice.

**2. Prepare the input files**

Place the following at the root of the `ACCESS-A-WEB` folder:
- Your Access file (`.accdb` or `.mdb`).
- Your logo in `JPG` or `PNG` format *(optional)*.

**3. Install the Jupyter extension in VS Code**

Open VS Code and install the **Jupyter** extension from:
- Menu `View > Extensions`, or
- Keyboard shortcut `Ctrl+Shift+X`.

**4. Open the project in VS Code**

```
File > Open Folder > [select the ACCESS-A-WEB folder]
```

**5. Open an integrated terminal**

```
Terminal > New Terminal   (or Ctrl+Shift+ñ)
```

**6. Create a virtual environment**

```bash
python -m venv .venv
```

**7. Activate the virtual environment**

```powershell
.venv\Scripts\Activate.ps1
```

**8. Install the dependencies**

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

**1. Open the notebook `ACCESS-A-WEB.ipynb`**

**2. Configure the parameters in the first cell** *(see the [Configuration parameters](#️-configuration-parameters) section)*

**3. Run all cells**

Click the **RUN ALL** button and, when prompted for the kernel, select:

1. `PYTHON ENVIRONMENTS`
2. `.VENV`

> ⚠️ **Warning:** Execution may take a while. If it stops, you can interrupt the kernel and run it again.

**4. Follow the instructions in the last cell**

Once execution is complete, the last cell of the notebook will indicate the steps to launch the generated web application.

---

## ⚙️ Configuration parameters

Modify these values in the **first cell** of the `ACCESS-A-WEB.ipynb` notebook:

| Parameter | Default value | Description |
|---|---|---|
| `INPUT_ACCDB` | `"Northwind.accdb"` | Input Access file (`.accdb` or `.mdb`) |
| `OUTPUT_SQLITE` | `"Northwind.sqlite"` | Name of the output SQLite file |
| `FLASK_OUTPUT_DIR` | `"app_web"` | Folder where the web application will be generated |
| `APP_TITLE` | `"Gestor de Base de dades"` | Title that will appear in the web application |
| `LOGO_PATH` | `"logo.png"` | Logo that will be displayed inside the web app |

**Example:**

```python
INPUT_ACCDB      = "ElMeuArxiu.accdb"
OUTPUT_SQLITE    = "ElMeuArxiu.sqlite"
FLASK_OUTPUT_DIR = "la_meva_app"
APP_TITLE        = "Arxiu Municipal"
LOGO_PATH        = "logo_ajuntament.png"
```

---

## 🌐 Deploying the application

Once the application has been generated in the folder indicated by `FLASK_OUTPUT_DIR`, it must be placed and configured on a **web server** to be accessed normally.

### 🔄 Modifying the SQLite database structure

If you need to modify tables or the structure of the generated database using the administrator's SQL query tool, follow this procedure:

1. Make the necessary changes to the SQLite file of the web app.
2. Make a **backup** of the SQLite file, preferably outside the `ACCESS-A-WEB` folder.
3. Paste a copy of the SQLite file inside the `ACCESS-A-WEB` folder (together with the logo). **No `.accdb` or `.mdb` file is needed.**
4. Delete the current web app folder.
5. Run `ACCESS-A-WEB.ipynb` again **cell by cell**, **without running cell 4** (the one that processes the original Access file).

---

## 📝 Important note

This tool **does not intend to replace** professional database management solutions. For complex administration tasks, various free software options are available online.

The administrator's SQL query tool is intended solely to facilitate **small batch modifications** to the data.

---
