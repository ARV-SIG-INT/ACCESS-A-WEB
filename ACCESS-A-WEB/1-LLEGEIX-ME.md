# ACCESS-A-WEB

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_App-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Base_de_dades-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-Editor-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![License](https://img.shields.io/badge/Llicència-GPLv3-blue?style=for-the-badge)

> Eina per transformar i visualitzar via web arxius **Microsoft Access** (`.accdb` / `.mdb`) que han quedat fora dels sistemes informàtics actuals, convertint-los en aplicacions web lleugeres amb **Flask** i **SQLite**.

---

## 📋 Taula de continguts

- [ACCESS-A-WEB](#access-a-web)
  - [📋 Taula de continguts](#-taula-de-continguts)
  - [📖 Descripció](#-descripció)
  - [🔧 Requisits previs](#-requisits-previs)
  - [🚀 Instal·lació](#-installació)
  - [▶️ Ús](#️-ús)
  - [⚙️ Paràmetres de configuració](#️-paràmetres-de-configuració)
  - [🌐 Desplegar l'aplicació](#-desplegar-laplicació)
    - [🔄 Modificar l'estructura de la base de dades SQLite](#-modificar-lestructura-de-la-base-de-dades-sqlite)
  - [📝 Nota important](#-nota-important)

---

## 📖 Descripció

**ACCESS-A-WEB** permet donar una segona vida als arxius Access oblidats de les organitzacions. A partir d'un fitxer `.accdb` o `.mdb`, genera automàticament:

- Una base de dades **SQLite** equivalent.
- Una **aplicació web Flask** completa per consultar i visualitzar les dades.
- Una eina de consultes SQL per a l'usuari administrador, orientada a petites modificacions en sèrie.

> ℹ️ **Nota:** L'objectiu d'aquesta eina **no és** ser una solució completa de gestió de bases de dades, sinó facilitar la recuperació i visualització de dades Access dins entorns web moderns. Només pretén poder-se estaviar l'adquisició de llicències de MS Office que incloguin ACCESS.

---

## 🔧 Requisits previs

| Eina | Descripció |
|---|---|
| [Python 3.x](https://www.python.org/downloads/) | Intèrpret de Python |
| [Visual Studio Code](https://code.visualstudio.com/download) | Editor de codi recomanat |
| Extensió **Jupyter** per a VS Code | Necessària per executar el notebook |

---

## 🚀 Instal·lació

**1. Descarrega i descomprimeix el projecte**

Desa la carpeta `ACCESS-A-WEB` al directori que prefereixis.

**2. Prepara els arxius d'entrada**

Col·loca a l'arrel de la carpeta `ACCESS-A-WEB`:
- El teu arxiu Access (`.accdb` o `.mdb`).
- El teu logotip en format `JPG` o `PNG` *(opcional)*.

**3. Instal·la l'extensió Jupyter a VS Code**

Obre VS Code i instal·la l'extensió **Jupyter** des de:
- Menú `View > Extensions`, o
- Combinació de tecles `Ctrl+Shift+X`.

**4. Obre el projecte a VS Code**

```
File > Open Folder > [selecciona la carpeta ACCESS-A-WEB]
```

**5. Obre un terminal integrat**

```
Terminal > New Terminal   (o Ctrl+Shift+ñ)
```

**6. Crea un entorn virtual**

```bash
python -m venv .venv
```

**7. Activa l'entorn virtual**

```powershell
.venv\Scripts\Activate.ps1
```

**8. Instal·la les dependències**

```bash
pip install -r requirements.txt
```

---

## ▶️ Ús

**1. Obre el notebook `ACCESS-A-WEB.ipynb`**

**2. Configura els paràmetres de la primera cel·la** *(vegeu la secció [Paràmetres de configuració](#️-paràmetres-de-configuració))*

**3. Executa totes les cel·les**

Clica el botó **RUN ALL** i, quan se sol·liciti el kernel, selecciona:

1. `PYTHON ENVIRONMENTS`
2. `.VENV`

> ⚠️ **Avís:** L'execució pot trigar una bona estona. Si s'atura, pots interrompre el kernel i tornar-lo a executar.

**4. Segueix les instruccions de l'última cel·la**

Un cop finalitzada l'execució, l'última cel·la del notebook indicarà els passos per posar en marxa l'aplicació web generada.

---

## ⚙️ Paràmetres de configuració

Modifica aquests valors a la **primera cel·la** del notebook `ACCESS-A-WEB.ipynb`:

| Paràmetre | Valor per defecte | Descripció |
|---|---|---|
| `INPUT_ACCDB` | `"Northwind.accdb"` | Arxiu Access d'entrada (`.accdb` o `.mdb`) |
| `OUTPUT_SQLITE` | `"Northwind.sqlite"` | Nom de l'arxiu SQLite de sortida |
| `FLASK_OUTPUT_DIR` | `"app_web"` | Carpeta on es generarà l'aplicació web |
| `APP_TITLE` | `"Gestor de Base de dades"` | Títol que apareixerà a l'aplicació web |
| `LOGO_PATH` | `"logo.png"` | Logotip que es mostrarà dins l'app web |

**Exemple:**

```python
INPUT_ACCDB      = "ElMeuArxiu.accdb"
OUTPUT_SQLITE    = "ElMeuArxiu.sqlite"
FLASK_OUTPUT_DIR = "la_meva_app"
APP_TITLE        = "Arxiu Municipal"
LOGO_PATH        = "logo_ajuntament.png"
```

---

## 🌐 Desplegar l'aplicació

Un cop generada l'aplicació a la carpeta indicada a `FLASK_OUTPUT_DIR`, cal col·locar-la i configurar-la en un **servidor web** per accedir-hi de forma habitual.

### 🔄 Modificar l'estructura de la base de dades SQLite

Si cal modificar taules o l'estructura de la base de dades generada mitjançant l'eina de consultes SQL de l'administrador, segueix aquest procediment:

1. Fes els canvis necessaris a l'arxiu SQLite de l'app web.
2. Fes una **còpia de seguretat** de l'arxiu SQLite, preferentment fora de la carpeta `ACCESS-A-WEB`.
3. Enganxa la còpia de l'arxiu SQLite dins la carpeta `ACCESS-A-WEB` (juntament amb el logo). **No cal cap fitxer `.accdb` o `.mdb`.**
4. Elimina la carpeta de l'app web actual.
5. Torna a executar `ACCESS-A-WEB.ipynb` **cel·la a cel·la**, **sense executar la cel·la 4** (la que processa l'arxiu Access original).

---

## 📝 Nota important

Aquesta eina **no pretén substituir** solucions professionals de gestió de bases de dades. Per a tasques complexes d'administració, existeixen diverses opcions de programari lliure disponibles a la xarxa.

L'eina de consultes SQL de l'administrador està pensada únicament per facilitar **petites modificacions en sèrie** sobre les dades.

---
