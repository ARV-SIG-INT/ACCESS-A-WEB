#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador d'aplicació Flask amb templates específics per taula, logo i títol.
Ús:
    python genera_app_flask.py --db-path exemple.db --output-dir app_generada --title "El meu títol" --logo logo.png
"""

import os
import json
import shutil
import argparse
import sqlite3

DEFAULT_USERS = [
    {"username": "admin01", "role": "admin", "password": "admin123"},
    {"username": "editor01", "role": "editor", "password": "editor123"},
    {"username": "lector01", "role": "lector", "password": "lector123"}
]

def parse_args():
    parser = argparse.ArgumentParser(description="Genera una aplicació Flask per gestionar una base de dades SQLite")
    parser.add_argument("--db-path", required=True, help="Ruta a la base de dades SQLite")
    parser.add_argument("--output-dir", required=True, help="Carpeta de sortida de l'aplicació")
    parser.add_argument("--title", required=True, help="Títol de l'aplicació")
    parser.add_argument("--logo", required=True, help="Ruta al fitxer del logo (deixa buit si no tens)")
    return parser.parse_args()

def detect_pk(columns):
    for col in columns:
        if col.get('pk') == 1:
            return col['name']
    for col in columns:
        if col['name'].lower() == 'id':
            return col['name']
    return 'rowid'

def is_autoincrement_pk(columns, pk_name):
    if pk_name == 'rowid':
        return True
    for col in columns:
        if col['name'] == pk_name and col.get('pk') == 1:
            return col['type'].upper() in ('INTEGER', 'INT', 'BIGINT', 'SMALLINT', 'TINYINT', 'INT2', 'INT8')
    return False

def get_schema_info(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row['name'] for row in cursor.fetchall()]
    schema = {}
    for table in tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = [dict(row) for row in cursor.fetchall()]
        pk_name = detect_pk(columns)
        schema[table] = {
            'columns': columns,
            'primary_key': pk_name,
            'auto_increment': is_autoincrement_pk(columns, pk_name)
        }
    conn.close()
    return schema

def generate_taula_templates(table, columns, pk_name, auto_increment, output_dir, header_html=""):
    templates_dir = os.path.join(output_dir, 'templates')
    os.makedirs(templates_dir, exist_ok=True)

    header_placeholder = "__HEADER_HTML__"
    
    
# ─── add_taula.html ────────────────────────────────────────────────────────
    add_template = f"""<!DOCTYPE html>
<html><head><title>Afegir a {table}</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body {{ background: #f8f9fa; }} .card {{ border-radius: 1rem; }}</style></head>
<body class="container mt-4">
{header_placeholder}
<div class="card"><div class="card-body">
  <a href="/table/{table}" class="btn btn-secondary mb-3">← Tornar</a>
  <h2>Afegir fila a {table}</h2>
  <form method="post">
"""
    for col in columns:
        if col['name'] == pk_name:
            add_template += f"""
    <div class="mb-3">
      <label>{col['name']} ({col['type']}) [PK - assignat automàticament]</label>
      <input type="number" name="{col['name']}" class="form-control bg-light" value="{{{{ next_id }}}}" readonly>
    </div>
"""
        else:
            input_type = "text"
            if col['type'].upper() in ('INTEGER', 'INT', 'REAL', 'FLOAT', 'NUMERIC'):
                input_type = "number"
            elif col['type'].upper() in ('DATE', 'DATETIME'):
                input_type = "date"
            add_template += f"""
    <div class="mb-3">
      <label>{col['name']} ({col['type']})</label>
      <input type="{input_type}" name="{col['name']}" class="form-control" value="">
    </div>
"""
    add_template += """
    <button type="submit" class="btn btn-primary">Desar</button>
  </form>
</div></div></body></html>"""
    add_template = add_template.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(templates_dir, f'add_{table}.html'), 'w', encoding='utf-8') as f:
        f.write(add_template)


# ─── edit_taula.html ───────────────────────────────────────────────────────
    edit_template = f"""<!DOCTYPE html>
<html><head><title>Editar {table}</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body {{ background: #f8f9fa; }} .card {{ border-radius: 1rem; }}</style></head>
<body class="container mt-4">
{header_placeholder}
<div class="card"><div class="card-body">
  <a href="/table/{table}" class="btn btn-secondary mb-3">← Tornar</a>
  <h2>Editar fila a {table}</h2>
  <form method="post">
"""
    for col in columns:
        if col['name'] == pk_name:
            edit_template += f"""
    <div class="mb-3">
      <label>{col['name']} ({col['type']}) [PK]</label>
      <input type="text" name="{col['name']}" class="form-control" value="{{{{ row['{col['name']}'] or '' }}}}" readonly>
    </div>
"""
        else:
            input_type = "text"
            if col['type'].upper() in ('INTEGER', 'INT', 'REAL', 'FLOAT', 'NUMERIC'):
                input_type = "number"
            elif col['type'].upper() in ('DATE', 'DATETIME'):
                input_type = "date"
            edit_template += f"""
    <div class="mb-3">
      <label>{col['name']} ({col['type']})</label>
      <input type="{input_type}" name="{col['name']}" class="form-control" value="{{{{ row['{col['name']}'] or '' }}}}">
    </div>
"""
    edit_template += """
    <button type="submit" class="btn btn-primary">Desar</button>
  </form>
</div></div></body></html>"""
    edit_template = edit_template.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(templates_dir, f'edit_{table}.html'), 'w', encoding='utf-8') as f:
        f.write(edit_template)


# ─── delete_taula.html ─────────────────────────────────────────────────────
    delete_template = f"""<!DOCTYPE html>
<html><head><title>Eliminar de {table}</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body {{ background: #f8f9fa; }} .card {{ border-radius: 1rem; }}</style></head>
<body class="container mt-4">
{header_placeholder}
<div class="card"><div class="card-body">
  <a href="/table/{table}" class="btn btn-secondary mb-3">← Tornar</a>
  <h2>Eliminar fila de {table}</h2>
  <p>Segur que vols eliminar el registre amb <strong>{pk_name} = {{{{ row['{pk_name}'] }}}}</strong>?</p>
  <form method="post">
    <button type="submit" class="btn btn-danger">Eliminar</button>
    <a href="/table/{table}" class="btn btn-secondary">Cancel·lar</a>
  </form>
</div></div></body></html>"""
    delete_template = delete_template.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(templates_dir, f'delete_{table}.html'), 'w', encoding='utf-8') as f:
        f.write(delete_template)

def generate_flask_app(db_path, output_dir, app_title, logo_path, initial_users):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'static'), exist_ok=True)

    logo_filename = None
    if logo_path and os.path.exists(logo_path):
        ext = os.path.splitext(logo_path)[1]
        logo_filename = f"logo{ext}"
        shutil.copy2(logo_path, os.path.join(output_dir, 'static', logo_filename))
        print(f"Logo copiat a static/{logo_filename}")
    elif logo_path:
        print(f"AVÍS: No s'ha trobat el fitxer '{logo_path}'. No es mostrarà cap logo.")

    users_list_str = json.dumps(initial_users, indent=4)
    logo_filename_str = f"'{logo_filename}'" if logo_filename else "None"

    header_html = """<div class="text-center mb-4">
      {% if logo_filename %}
        <img src="{{ url_for('static', filename=logo_filename) }}" alt="Logo" class="img-fluid" style="max-height: 100px;">
      {% endif %}
      <h1 class="display-5 fw-bold text-primary">{{ app_title }}</h1>
      <hr class="my-2">
    </div>"""

    schema_info = get_schema_info(db_path)
    print("Generant templates específics per a les taules:", list(schema_info.keys()))
    for table, info in schema_info.items():
        generate_taula_templates(table, info['columns'], info['primary_key'], info['auto_increment'], output_dir, header_html)


# ─── GENERACIÓ DE app.py ───────────────────────────────────────────────────
    app_template = """
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, flash, session
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'CLAU-SECRETA'

DATABASE = '__DB_PATH__'
USER_DB = 'users.db'

INITIAL_USERS = __USERS_LIST__

APP_TITLE = '__APP_TITLE__'
LOGO_FILENAME = __LOGO_FILENAME__

def init_user_db():
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL)')
    for user in INITIAL_USERS:
        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (user['username'], user['password'], user['role']))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

def get_user_db():
    db = getattr(g, '_user_db', None)
    if db is None:
        db = g._user_db = sqlite3.connect(USER_DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    user_db = getattr(g, '_user_db', None)
    if user_db is not None:
        user_db.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
        db.row_factory = sqlite3.Row
    return db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Has d'iniciar sessió", 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Accés denegat: només per a administradors', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def editor_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        if role not in ['admin', 'editor']:
            flash('Accés denegat: només per a editors o administradors', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def detect_pk(columns):
    for col in columns:
        if col.get('pk') == 1:
            return col['name']
    for col in columns:
        if col['name'].lower() == 'id':
            return col['name']
    return 'rowid'

def is_autoincrement_pk(columns, pk_name):
    if pk_name == 'rowid':
        return True
    for col in columns:
        if col['name'] == pk_name and col.get('pk') == 1:
            return col['type'].upper() in ('INTEGER', 'INT', 'BIGINT', 'SMALLINT', 'TINYINT', 'INT2', 'INT8')
    return False

def get_schema():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row['name'] for row in cursor.fetchall()]
    schema = {}
    for table in tables:
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = [dict(row) for row in cursor.fetchall()]
        pk = detect_pk(columns)
        schema[table] = {
            'columns': columns,
            'primary_key': pk,
            'auto_increment': is_autoincrement_pk(columns, pk)
        }
    return schema

def get_visible_tables(all_tables):
    visible = session.get('visible_tables')
    if visible is None:
        return list(all_tables)
    return [t for t in visible if t in all_tables]

def get_visible_columns(table_name, all_columns):
    visible = session.get('visible_columns', {}).get(table_name)
    if visible is None:
        return [col['name'] for col in all_columns]
    pk = next((col['name'] for col in all_columns if col.get('pk') == 1), None)
    if pk and pk not in visible:
        visible.append(pk)
    return visible

def get_table_data(table, search_term=None, order_by=None):
    db = get_db()
    cursor = db.cursor()
    schema = get_schema()
    all_columns = [col['name'] for col in schema[table]['columns']]
    pk = schema[table]['primary_key']
    select_cols = all_columns.copy()
    if pk == 'rowid' and 'rowid' not in select_cols:
        select_cols.append('rowid')
    if pk == 'rowid':
        cols_quoted = [f'"{col}"' for col in all_columns]
        select_str = ', '.join(cols_quoted) + ', rowid AS rowid'
    else:
        select_str = ', '.join([f'"{col}"' for col in select_cols])
    if search_term:
        conditions = ' OR '.join([f'CAST("{col}" AS TEXT) LIKE ?' for col in all_columns])
        like_pattern = f'%{search_term}%'
        params = [like_pattern] * len(all_columns)
        if order_by and order_by in all_columns:
            query = f'SELECT {select_str} FROM "{table}" WHERE {conditions} ORDER BY "{order_by}"'
        else:
            query = f'SELECT {select_str} FROM "{table}" WHERE {conditions}'
        cursor.execute(query, params)
    else:
        if order_by and order_by in all_columns:
            query = f'SELECT {select_str} FROM "{table}" ORDER BY "{order_by}"'
        else:
            query = f'SELECT {select_str} FROM "{table}"'
        cursor.execute(query)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_user_db()
        c = conn.cursor()
        c.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = username
            session.setdefault('visible_tables', None)
            session.setdefault('visible_columns', {})
            flash('Inici de sessió correcte', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuari o contrasenya incorrectes', 'danger')
    return render_template('login.html', app_title=APP_TITLE, logo_filename=LOGO_FILENAME)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessió tancada', 'info')
    return redirect(url_for('login'))

# ------------------ Gestió d'usuaris (admin) ------------------
@app.route('/admin/users')
@login_required
@admin_required
def manage_users():
    db = get_user_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, role FROM users ORDER BY id")
    users = cursor.fetchall()
    return render_template('users.html', users=users, current_user_id=session['user_id'], app_title=APP_TITLE, logo_filename=LOGO_FILENAME)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_user_db()
        try:
            db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            db.commit()
            flash('Usuari creat correctament', 'success')
            return redirect(url_for('manage_users'))
        except sqlite3.IntegrityError:
            flash("El nom d'usuari ja existeix", 'danger')
    return render_template('user_form.html', action='add', user=None, app_title=APP_TITLE, logo_filename=LOGO_FILENAME)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    db = get_user_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        try:
            db.execute("UPDATE users SET username=?, password=?, role=? WHERE id=?", (username, password, role, user_id))
            db.commit()
            flash('Usuari actualitzat', 'success')
            if user_id == session['user_id']:
                session['username'] = username
            return redirect(url_for('manage_users'))
        except sqlite3.IntegrityError:
            flash("El nom d'usuari ja existeix", 'danger')
    else:
        user = db.execute("SELECT id, username, password, role FROM users WHERE id=?", (user_id,)).fetchone()
        if not user:
            flash('Usuari no trobat', 'danger')
            return redirect(url_for('manage_users'))
        return render_template('user_form.html', action='edit', user=user, app_title=APP_TITLE, logo_filename=LOGO_FILENAME)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('No pots eliminar el teu propi usuari', 'danger')
        return redirect(url_for('manage_users'))
    db = get_user_db()
    db.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    flash('Usuari eliminat', 'success')
    return redirect(url_for('manage_users'))

# ------------------ Pàgina principal ------------------
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    schema = get_schema()
    all_tables = list(schema.keys())
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'show_all_tables':
            visible_tables = all_tables.copy()
        elif action == 'hide_all_tables':
            visible_tables = []
        else:
            visible_tables = request.form.getlist('visible_tables')
        session['visible_tables'] = visible_tables
        session.modified = True
        flash('Preferències de taules actualitzades', 'success')
        return redirect(url_for('index'))
    visible_tables = get_visible_tables(all_tables)
    return render_template('index.html', all_tables=all_tables, visible_tables=visible_tables, role=session.get('role'), app_title=APP_TITLE, logo_filename=LOGO_FILENAME)

# ------------------ Visualització de taula ------------------
@app.route('/table/<table_name>', methods=['GET', 'POST'])
@login_required
def view_table(table_name):
    schema = get_schema()
    if table_name not in schema:
        flash('Taula no trobada', 'danger')
        return redirect(url_for('index'))
    all_columns = schema[table_name]['columns']
    pk = schema[table_name]['primary_key']
    column_names = [col['name'] for col in all_columns]

    if request.method == 'POST' and session.get('role') in ['admin', 'editor', 'lector']:
        action = request.form.get('action')
        if action == 'show_all':
            visible = column_names.copy()
        elif action == 'hide_all':
            visible = [pk] if pk else []
        else:
            visible = request.form.getlist('visible_columns')
            if pk and pk not in visible:
                visible.append(pk)
        if 'visible_columns' not in session:
            session['visible_columns'] = {}
        session['visible_columns'][table_name] = visible
        session.modified = True
        flash('Preferències de columnes actualitzades', 'success')
        return redirect(url_for('view_table', table_name=table_name))

    visible_cols = get_visible_columns(table_name, all_columns)
    order_by = request.args.get('order_by')
    search_term = request.args.get('search', '').strip()
    rows = get_table_data(table_name, search_term if search_term else None, order_by)

    return render_template('table_view.html',
                           table=table_name,
                           all_columns=all_columns,
                           visible_columns=visible_cols,
                           rows=rows,
                           pk=pk,
                           role=session.get('role'),
                           search_term=search_term,
                           app_title=APP_TITLE,
                           logo_filename=LOGO_FILENAME)

# ------------------ Afegir fila (modificat) ------------------
@app.route('/table/<table_name>/add', methods=['GET', 'POST'])
@login_required
@editor_or_admin_required
def add_row(table_name):
    schema = get_schema()
    if table_name not in schema:
        flash('Taula no trobada', 'danger')
        return redirect(url_for('index'))
    table_info = schema[table_name]
    columns = table_info['columns']
    pk = table_info['primary_key']

    # Escollir template
    template_name = f'add_{table_name}.html'
    template_path = os.path.join(app.template_folder, template_name)
    if not os.path.exists(template_path):
        template_name = 'row_form.html'

    # Calcular next_id per preomplir el formulari (GET)
    def calcular_next_id(connexio):
        # Usem sempre MAX(rowid) que és el comptador intern real de SQLite,
        # independent del nom i valor de la columna PK declarada.
        r = connexio.execute(f'SELECT MAX(rowid) FROM "{table_name}"').fetchone()
        max_val = r[0]
        return (int(max_val) + 1) if max_val is not None else 1

    next_id = 1
    try:
        next_id = calcular_next_id(get_db())
    except Exception as e:
        app.logger.warning(f"No s'ha pogut calcular el seguent ID: {e}")

    if request.method == 'POST':
        db = get_db()
        try:
            db.execute('BEGIN EXCLUSIVE')
            # Recalcular dins la transacció per garantir valor correcte
            next_id = calcular_next_id(db)

            insertable_cols = []
            values = []
            for col in columns:
                col_name = col['name']
                if col_name == pk:
                    insertable_cols.append(col_name)
                    values.append(next_id)
                else:
                    val = request.form.get(col_name)
                    if val == '' and col['type'].upper() not in ('TEXT', 'VARCHAR', 'CHAR', 'CLOB'):
                        val = None
                    insertable_cols.append(col_name)
                    values.append(val)

            col_names_quoted = [f'"{c}"' for c in insertable_cols]
            placeholders = ','.join(['?' for _ in values])
            query = f'INSERT INTO "{table_name}" ({",".join(col_names_quoted)}) VALUES ({placeholders})'
            db.execute(query, values)
            db.execute('COMMIT')
            flash('Fila afegida correctament', 'success')
            return redirect(url_for('view_table', table_name=table_name))

        except Exception as e:
            try:
                db.execute('ROLLBACK')
            except Exception:
                pass
            flash(f'Error en afegir la fila: {e}', 'danger')

    # GET: mostrar formulari amb next_id preomplert
    return render_template(template_name,
                           table=table_name,
                           columns=columns,
                           pk=pk,
                           row={pk: next_id},
                           next_id=next_id,
                           action='add',
                           app_title=APP_TITLE,
                           logo_filename=LOGO_FILENAME)

# ------------------ Editar fila ------------------
@app.route('/table/<table_name>/edit/<row_id>', methods=['GET', 'POST'])
@login_required
@editor_or_admin_required
def edit_row(table_name, row_id):
    schema = get_schema()
    if table_name not in schema:
        flash('Taula no trobada', 'danger')
        return redirect(url_for('index'))
    table_info = schema[table_name]
    pk = table_info['primary_key']
    if not pk:
        flash('Aquesta taula no té clau primària; no es pot editar', 'danger')
        return redirect(url_for('view_table', table_name=table_name))
    db = get_db()
    columns = table_info['columns']
    
    # Escollir template
    template_name = f'edit_{table_name}.html'
    template_path = os.path.join(app.template_folder, template_name)
    if not os.path.exists(template_path):
        template_name = 'row_form.html'
    
    if request.method == 'POST':
        set_clauses = []
        values = []
        for col in columns:
            if col['name'] == pk:
                continue  # no actualitzar la PK
            val = request.form.get(col['name'])
            # Convertir buit a None per a columnes no text
            if val == '' and col['type'].upper() not in ('TEXT', 'VARCHAR', 'CHAR', 'CLOB'):
                val = None
            set_clauses.append(f'"{col["name"]}" = ?')
            values.append(val)
        values.append(row_id)  # per la clàusula WHERE
        query = f'UPDATE "{table_name}" SET {", ".join(set_clauses)} WHERE "{pk}" = ?'
        try:
            db.execute(query, values)
            db.commit()
            flash('Fila actualitzada', 'success')
            return redirect(url_for('view_table', table_name=table_name))        
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('view_table', table_name=table_name))
    else:
        # GET: carregar dades
        if pk == 'rowid':
            row = db.execute(f'SELECT *, rowid AS rowid FROM "{table_name}" WHERE rowid = ?', (row_id,)).fetchone()
        else:
            row = db.execute(f'SELECT * FROM "{table_name}" WHERE "{pk}" = ?', (row_id,)).fetchone()
        if not row:
            flash('Fila no trobada', 'danger')
            return redirect(url_for('view_table', table_name=table_name))
        row_dict = dict(row)
        if pk == 'rowid' and 'rowid' not in row_dict:
            row_dict['rowid'] = row_id
        return render_template(template_name,
                               table=table_name,
                               columns=columns,
                               pk=pk,
                               row=row_dict,
                               action='edit',
                               app_title=APP_TITLE,
                               logo_filename=LOGO_FILENAME)

# ------------------ Eliminar fila ------------------
@app.route('/table/<table_name>/delete/<row_id>', methods=['GET', 'POST'])
@login_required
@editor_or_admin_required
def delete_row(table_name, row_id):
    schema = get_schema()
    if table_name not in schema:
        flash('Taula no trobada', 'danger')
        return redirect(url_for('index'))
    pk = schema[table_name]['primary_key']
    if not pk:
        flash('No es pot eliminar sense clau primària', 'danger')
        return redirect(url_for('view_table', table_name=table_name))
    db = get_db()
    
    # Escollir template
    template_name = f'delete_{table_name}.html'
    template_path = os.path.join(app.template_folder, template_name)
    if not os.path.exists(template_path):
        template_name = 'confirm_delete.html'
    
    if request.method == 'POST':
        try:
            if pk == 'rowid':
                db.execute(f'DELETE FROM "{table_name}" WHERE rowid = ?', (row_id,))
            else:
                db.execute(f'DELETE FROM "{table_name}" WHERE "{pk}" = ?', (row_id,))
            db.commit()
            flash('Fila eliminada', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('view_table', table_name=table_name))
    else:
        # GET: mostrar confirmació
        if pk == 'rowid':
            row = db.execute(f'SELECT *, rowid AS rowid FROM "{table_name}" WHERE rowid = ?', (row_id,)).fetchone()
        else:
            row = db.execute(f'SELECT * FROM "{table_name}" WHERE "{pk}" = ?', (row_id,)).fetchone()
        if not row:
            flash('Fila no trobada', 'danger')
            return redirect(url_for('view_table', table_name=table_name))
        row_dict = dict(row)
        if pk == 'rowid' and 'rowid' not in row_dict:
            row_dict['rowid'] = row_id
        return render_template(template_name,
                               table=table_name,
                               row=row_dict,
                               pk=pk,
                               app_title=APP_TITLE,
                               logo_filename=LOGO_FILENAME)

# ------------------ Consola SQL (admin) ------------------
@app.route('/admin/sql', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_sql():
    result = None
    error = None
    if request.method == 'POST':
        sql = request.form['sql']
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute(sql)
            if sql.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                if result:
                    result = [dict(row) for row in result]
            else:
                db.commit()
                flash('Sentència executada correctament', 'success')
        except Exception as e:
            error = str(e)
    return render_template('admin_sql.html', result=result, error=error, app_title=APP_TITLE, logo_filename=LOGO_FILENAME)

if __name__ == '__main__':
    init_user_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
    app_code = app_template.replace('__DB_PATH__', db_path)
    app_code = app_code.replace('__USERS_LIST__', users_list_str)
    app_code = app_code.replace('__APP_TITLE__', app_title)
    app_code = app_code.replace('__LOGO_FILENAME__', logo_filename_str)

    with open(os.path.join(output_dir, 'app.py'), 'w', encoding='utf-8') as f:
        f.write(app_code)


# ─── GENERACIÓ DE PLANTILLES HTML COMUNES ──────────────────────────────────
    login_html = """<!DOCTYPE html>
<html><head><title>Inici de sessió</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; } .card { border-radius: 1rem; box-shadow: 0 1rem 3rem rgba(0,0,0,0.2); }</style></head>
<body class="d-flex align-items-center"><div class="container"><div class="row justify-content-center"><div class="col-md-6 col-lg-5">
<div class="card shadow-lg"><div class="card-body p-5">
__HEADER_HTML__
<h2 class="text-center mb-4">Inici de sessió</h2>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}<div class="alert alert-{{ category }}">{{ message }}</div>{% endfor %}
{% endwith %}
<form method="post"><div class="mb-3"><label>Usuari</label><input type="text" name="username" class="form-control" required></div>
<div class="mb-3"><label>Contrasenya</label><input type="password" name="password" class="form-control" required></div>
<button type="submit" class="btn btn-primary w-100">Entrar</button></form>
</div></div></div></div></div></body></html>"""
    login_html = login_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'login.html'), 'w', encoding='utf-8') as f:
        f.write(login_html)

    index_html = """<!DOCTYPE html>
<html><head><title>Taules</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1); }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="d-flex justify-content-between align-items-center mb-3">
  <div>
    {% if role == 'admin' %}
      <a href="/admin/users" class="btn btn-info me-2">Gestió d'usuaris</a>
      <a href="/admin/sql" class="btn btn-warning me-2">Executar SQL</a>
    {% endif %}
  </div>
  <a href="/logout" class="btn btn-secondary">Tancar sessió ({{ role }})</a>
</div>
<div class="card"><div class="card-body">
  <form method="post" class="mb-3">
    <label class="fw-bold">Taules a mostrar:</label><br>
    <div class="row">
      <div class="col-md-8">
        {% for table in all_tables %}
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" name="visible_tables" value="{{ table }}" id="table_{{ table }}" {% if table in visible_tables %}checked{% endif %}>
            <label class="form-check-label" for="table_{{ table }}">{{ table }}</label>
          </div>
        {% endfor %}
      </div>
      <div class="col-md-4 text-end">
        <button type="submit" name="action" value="update_tables" class="btn btn-primary">Aplicar selecció</button>
        <button type="submit" name="action" value="show_all_tables" class="btn btn-secondary">Mostrar tot</button>
        <button type="submit" name="action" value="hide_all_tables" class="btn btn-secondary">Ocultar taules</button>
      </div>
    </div>
  </form>
  <h2 class="mt-3">Taules visibles</h2>
  {% if visible_tables %}
    <ul class="list-group">
      {% for table in visible_tables %}
        <li class="list-group-item"><a href="/table/{{ table }}">{{ table }}</a></li>
      {% endfor %}
    </ul>
  {% else %}
    <p class="text-muted">No hi ha taules visibles. Selecciona alguna a dalt.</p>
  {% endif %}
</div></div></body></html>"""
    index_html = index_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)

    table_view_html = """<!DOCTYPE html>
<html><head><title>Taula: {{ table }}</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1); }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="d-flex justify-content-between mb-3">
  <a href="/" class="btn btn-secondary">← Inici</a>
  <a href="/logout" class="btn btn-secondary">Sortir</a>
</div>
<div class="card"><div class="card-body">
  <h2 class="mb-3">Taula: {{ table }}</h2>
  <form method="get" class="row g-3 mb-3">
    <div class="col-auto"><input type="text" name="search" class="form-control" placeholder="Cerca..." value="{{ search_term }}"></div>
    <div class="col-auto"><button type="submit" class="btn btn-primary">Cercar</button></div>
    {% if search_term %}<div class="col-auto"><a href="?" class="btn btn-secondary">Netejar</a></div>{% endif %}
  </form>
  <form method="post" class="mb-3 border p-3 rounded">
    <label class="fw-bold">Columnes a mostrar:</label><br>
    {% for col in all_columns %}
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="checkbox" name="visible_columns" value="{{ col.name }}" id="col_{{ col.name }}" {% if col.name in visible_columns %}checked{% endif %}>
        <label class="form-check-label" for="col_{{ col.name }}">{{ col.name }} ({{ col.type }})</label>
      </div>
    {% endfor %}
    <div class="mt-2 text-end">
      <button type="submit" name="action" value="update" class="btn btn-primary">Aplicar selecció</button>
      <button type="submit" name="action" value="show_all" class="btn btn-secondary">Mostrar tot</button>
      <button type="submit" name="action" value="hide_all" class="btn btn-secondary">Ocultar camps</button>
    </div>
  </form>
  {% if role in ['admin', 'editor'] %}
    <div class="mb-3"><a href="/table/{{ table }}/add" class="btn btn-success">➕ Afegir fila</a></div>
  {% endif %}
  {% if rows %}
  <div class="table-responsive"><table class="table table-striped table-hover">
    <thead class="table-dark"><tr>
      {% for col in all_columns %}
        {% if col.name in visible_columns %}
          <th><a href="?order_by={{ col.name }}{% if search_term %}&search={{ search_term }}{% endif %}" class="text-white">{{ col.name }}</a> ({{ col.type }})</th>
        {% endif %}
      {% endfor %}
      <th>Accions</th>
    </tr></thead>
    <tbody>
      {% for row in rows %}
      <tr>
        {% for col in all_columns %}
          {% if col.name in visible_columns %}
            <td>{{ row[col.name] if row[col.name] is not none else '' }}</td>
          {% endif %}
        {% endfor %}
        <td>
          {% if role in ['admin', 'editor'] %}
            {% set row_id = row[pk] if pk in row else row.get('rowid', '') %}
            <a href="{{ url_for('edit_row', table_name=table, row_id=row_id) }}" class="btn btn-sm btn-primary">Editar</a>
            <form method="post" action="{{ url_for('delete_row', table_name=table, row_id=row_id) }}" style="display:inline">
            <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Segur?')">Eliminar</button>
            </form>
          {% else %}
            <span class="text-muted">Només lectura</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table></div>
  {% else %}
    <p>No hi ha dades. {% if search_term %}Prova un altre terme de cerca.{% endif %}</p>
  {% endif %}
</div></div></body></html>"""
    table_view_html = table_view_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'table_view.html'), 'w', encoding='utf-8') as f:
        f.write(table_view_html)

    row_form_html = """<!DOCTYPE html>
<html><head><title>{{ action | capitalize }} fila</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="card"><div class="card-body">
  <a href="/table/{{ table }}" class="btn btn-secondary mb-3">← Tornar</a>
  <h2>{{ action | capitalize }} fila a {{ table }}</h2>
  <form method="post">
    {% for col in columns %}
      {% if col['name'] == pk %}
        <div class="mb-3">
          <label>{{ col['name'] }} ({{ col['type'] }}) [PK - assignat automàticament]</label>
          <input type="number" name="{{ col['name'] }}" class="form-control bg-light"
                 value="{{ row[col['name']] if row else '' }}" readonly>
        </div>
      {% else %}
      <div class="mb-3">
        <label>{{ col['name'] }} ({{ col['type'] }})</label>
        <input type="text" name="{{ col['name'] }}" class="form-control" value="{{ row[col['name']] if row else '' }}">
      </div>
      {% endif %}
    {% endfor %}
    <button type="submit" class="btn btn-primary">Desar</button>
  </form>
</div></div></body></html>"""
    row_form_html = row_form_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'row_form.html'), 'w', encoding='utf-8') as f:
        f.write(row_form_html)

    confirm_delete_html = """<!DOCTYPE html>
<html><head><title>Eliminar</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="card"><div class="card-body">
  <a href="/table/{{ table }}" class="btn btn-secondary mb-3">← Tornar</a>
  <h2>Eliminar fila de {{ table }}</h2>
  <p>Segur que vols eliminar el registre amb <strong>{{ pk }} = {{ row[pk] }}</strong>?</p>
  <form method="post">
    <button type="submit" class="btn btn-danger">Eliminar</button>
    <a href="/table/{{ table }}" class="btn btn-secondary">Cancel·lar</a>
  </form>
</div></div></body></html>"""
    confirm_delete_html = confirm_delete_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'confirm_delete.html'), 'w', encoding='utf-8') as f:
        f.write(confirm_delete_html)

    admin_sql_html = """<!DOCTYPE html>
<html><head><title>SQL</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="card"><div class="card-body">
  <a href="/" class="btn btn-secondary mb-3">← Inici</a>
  <h2>Consola SQL (Admin)</h2>
  <form method="post">
    <div class="mb-3"><textarea name="sql" rows="6" class="form-control font-monospace" placeholder="SELECT * FROM usuaris;"></textarea></div>
    <button type="submit" class="btn btn-danger">Executar</button>
  </form>
  {% if error %}<div class="alert alert-danger mt-3">{{ error }}</div>{% endif %}
  {% if result %}
    <h3 class="mt-3">Resultat</h3>
    <div class="table-responsive"><table class="table table-sm table-bordered">
      <thead><tr>{% for key in result[0].keys() %}<th>{{ key }}</th>{% endfor %}</tr></thead>
      <tbody>{% for row in result %}<tr>{% for value in row.values() %}<td>{{ value }}</td>{% endfor %}</tr>{% endfor %}</tbody>
    </table></div>
  {% endif %}
</div></div></body></html>"""
    admin_sql_html = admin_sql_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'admin_sql.html'), 'w', encoding='utf-8') as f:
        f.write(admin_sql_html)

    users_html = """<!DOCTYPE html>
<html><head><title>Gestió d'usuaris</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="card"><div class="card-body">
  <a href="/" class="btn btn-secondary mb-3">← Inici</a>
  <h2>Gestió d'usuaris</h2>
  <div class="mb-2"><a href="/admin/users/add" class="btn btn-success">➕ Crear usuari</a></div>
  <div class="table-responsive"><table class="table table-striped table-hover">
    <thead class="table-dark"><tr><th>ID</th><th>Nom d'usuari</th><th>Rol</th><th>Accions</th></tr></thead>
    <tbody>
      {% for user in users %}
      <tr>
        <td>{{ user.id }}</td>
        <td>{{ user.username }}</td>
        <td>{{ user.role }}</td>
        <td>
          <a href="/admin/users/edit/{{ user.id }}" class="btn btn-sm btn-primary">Editar</a>
          {% if user.id != current_user_id %}
            <form method="post" action="/admin/users/delete/{{ user.id }}" style="display:inline">
              <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('Eliminar aquest usuari?')">Eliminar</button>
            </form>
          {% else %}
            <span class="text-muted">(tu)</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table></div>
</div></div></body></html>"""
    users_html = users_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'users.html'), 'w', encoding='utf-8') as f:
        f.write(users_html)

    user_form_html = """<!DOCTYPE html>
<html><head><title>{{ action | capitalize }} usuari</title><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
<style>body { background: #f8f9fa; } .card { border-radius: 1rem; }</style></head>
<body class="container mt-4">
__HEADER_HTML__
<div class="card"><div class="card-body">
  <a href="/admin/users" class="btn btn-secondary mb-3">← Tornar</a>
  <h2>{{ action | capitalize }} usuari</h2>
  <form method="post">
    <div class="mb-3">
      <label>Nom d'usuari</label>
      <input type="text" name="username" class="form-control" value="{{ user.username if user else '' }}" required>
    </div>
    <div class="mb-3">
      <label>Contrasenya</label>
      <input type="password" name="password" class="form-control" value="{{ user.password if user else '' }}" required>
    </div>
    <div class="mb-3">
      <label>Rol</label>
      <select name="role" class="form-control">
        <option value="admin" {% if user and user.role == 'admin' %}selected{% endif %}>Admin</option>
        <option value="editor" {% if user and user.role == 'editor' %}selected{% endif %}>Editor</option>
        <option value="lector" {% if user and user.role == 'lector' %}selected{% endif %}>Lector</option>
      </select>
    </div>
    <button type="submit" class="btn btn-primary">Desar</button>
  </form>
</div></div></body></html>"""
    user_form_html = user_form_html.replace('__HEADER_HTML__', header_html)
    with open(os.path.join(output_dir, 'templates', 'user_form.html'), 'w', encoding='utf-8') as f:
        f.write(user_form_html)

    with open(os.path.join(output_dir, 'requirements.txt'), 'w') as f:
        f.write("Flask\n")

    dockerfile = f'''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY {os.path.basename(db_path)} ./
EXPOSE 5000
CMD ["python", "app.py"]
'''
    with open(os.path.join(output_dir, 'Dockerfile'), 'w') as f:
        f.write(dockerfile)

    readme_lines = [
        "# Aplicació Flask amb templates específics per taula",
        "",
        "## Execució",
        "1. `pip install -r requirements.txt`",
        "2. `python app.py`",
        "3. Obre `http://localhost:5000`",
        "",
        "## Usuaris per defecte",
    ]
    for u in initial_users:
        readme_lines.append(f"- {u['username']} / {u['password']} (rol {u['role']})")
    readme_lines.extend([
        "",
        "## Funcionalitats",
        "- **Admin**: CRUD de dades, consola SQL, gestió d'usuaris.",
        "- **Editor**: CRUD de dades (sense SQL ni gestió d'usuaris).",
        "- **Lector**: només visualització.",
        "- **Templates específics per a cada taula** per a add/edit/delete (generats automàticament).",
        "- Logo i títol centrats.",
        "",
        "## Docker",
        "```bash",
        "docker build -t flask-app .",
        "docker run -p 5000:5000 flask-app",
        "```",
    ])
    readme = "\n".join(readme_lines)
    with open(os.path.join(output_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f"✅ Aplicació generada a '{output_dir}'")

def main():
    args = parse_args()
    generate_flask_app(args.db_path, args.output_dir, args.title, args.logo, DEFAULT_USERS)

if __name__ == "__main__":
    main()