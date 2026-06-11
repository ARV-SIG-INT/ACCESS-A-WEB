#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
accdb_a_sqlite.py
==================
Migra una base de dades Microsoft Access (.accdb / .mdb) a SQLite,
conservant l'estructura de taules, els tipus de dades i les relacions
(claus foranes) entre elles.

Dependències:
    pip install pyodbc        # connexió a Access (Windows)
    # O bé:
    pip install mdbtools-python  # wrapper de mdbtools (Linux/macOS)
    # SQLite ve inclòs a la biblioteca estàndard de Python (sqlite3)

Ús:
    python accdb_to_sqlite.py --input arxiu.accdb --output base_de_dades.sqlite
    python accdb_to_sqlite.py --input arxiu.accdb --output base_de_dades.sqlite --verbose
"""

import sqlite3
import argparse
import logging
import sys
import os
import re
from typing import Any


# ─── Detecció del connector disponible ─────────────────────────────────────

def get_access_connector():
    """Retorna 'pyodbc' o 'mdbtools' segons el que estigui disponible."""
    try:
        import pyodbc
        return "pyodbc"
    except ImportError:
        pass
    try:
        import subprocess
        result = subprocess.run(["mdb-tables", "--version"], capture_output=True)
        if result.returncode == 0:
            return "mdbtools"
    except FileNotFoundError:
        pass
    raise RuntimeError(
        "No s'ha trobat cap connector per a Access.\n"
        "  Windows : pip install pyodbc\n"
        "  Linux/macOS: sudo apt install mdbtools  (o brew install mdbtools)\n"
        "               pip install mdbtools-python  (opcional)"
    )


# ─── Adaptació de tipus de dades Access → SQLite ────────────────────────────

ACCESS_TYPE_MAP = {
    "BYTE":       "INTEGER",
    "INTEGER":    "INTEGER",
    "LONG":       "INTEGER",
    "SINGLE":     "REAL",
    "DOUBLE":     "REAL",
    "DECIMAL":    "REAL",
    "CURRENCY":   "REAL",
    "AUTONUMBER": "INTEGER",
    "TEXT":       "TEXT",
    "MEMO":       "TEXT",
    "CHAR":       "TEXT",
    "VARCHAR":    "TEXT",
    "LONGTEXT":   "TEXT",
    "DATETIME":   "TEXT", 
    "DATE":       "TEXT",
    "TIME":       "TEXT",
    "BIT":        "INTEGER", 
    "YESNO":      "INTEGER",
    "BINARY":     "BLOB",
    "LONGBINARY": "BLOB",
    "OLE":        "BLOB",
    "UNKNOWN":    "TEXT",
}

def map_type(access_type: str) -> str:
    key = re.sub(r"\s*\(.*\)", "", access_type).upper().strip()
    return ACCESS_TYPE_MAP.get(key, "TEXT")


# ─── Classes de connexió ─────────────────────────────────────────────────────

class PyodbcAccessReader:
    """Lector per a Windows via pyodbc."""

    def __init__(self, accdb_path: str):
        import pyodbc
        conn_str = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={os.path.abspath(accdb_path)};"
        )
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

    def get_table_names(self) -> list[str]:
        tables = [
            row.table_name
            for row in self.cursor.tables(tableType="TABLE")
            if not row.table_name.startswith("MSys")
        ]
        return tables

    def get_columns(self, table: str) -> list[dict]:
        """
        Usa SELECT * WHERE 1=0 en lloc de cursor.columns() per evitar
        el UnicodeDecodeError 'utf-16-le' que pyodbc llança en llegir
        metadades de taules amb noms especials o codificació Windows.
        Els tipus es mapegen des dels codis numèrics de pyodbc.
        """
        import pyodbc
        
        SQL_TYPE_NAMES = {
            pyodbc.SQL_CHAR:            "CHAR",
            pyodbc.SQL_VARCHAR:         "VARCHAR",
            pyodbc.SQL_LONGVARCHAR:     "MEMO",
            pyodbc.SQL_WCHAR:           "TEXT",
            pyodbc.SQL_WVARCHAR:        "TEXT",
            pyodbc.SQL_WLONGVARCHAR:    "MEMO",
            pyodbc.SQL_DECIMAL:         "DECIMAL",
            pyodbc.SQL_NUMERIC:         "DECIMAL",
            pyodbc.SQL_SMALLINT:        "INTEGER",
            pyodbc.SQL_INTEGER:         "LONG",
            pyodbc.SQL_REAL:            "SINGLE",
            pyodbc.SQL_FLOAT:           "DOUBLE",
            pyodbc.SQL_DOUBLE:          "DOUBLE",
            pyodbc.SQL_BIT:             "BIT",
            pyodbc.SQL_TINYINT:         "BYTE",
            pyodbc.SQL_BIGINT:          "LONG",
            pyodbc.SQL_BINARY:          "BINARY",
            pyodbc.SQL_VARBINARY:       "BINARY",
            pyodbc.SQL_LONGVARBINARY:   "LONGBINARY",
            pyodbc.SQL_TYPE_DATE:       "DATE",
            pyodbc.SQL_TYPE_TIME:       "TIME",
            pyodbc.SQL_TYPE_TIMESTAMP:  "DATETIME",
        }
        try:
            self.cursor.execute(f"SELECT * FROM [{table}] WHERE 1=0")
        except Exception as e:
            raise RuntimeError(f"No es pot llegir l'esquema de '{table}': {e}")

        cols = []
        for desc in self.cursor.description:
            name     = desc[0]
            type_cod = desc[1]
            null_ok  = desc[6]
            type_name = SQL_TYPE_NAMES.get(type_cod, "TEXT")
            cols.append({
                "name":     name,
                "type":     type_name,
                "nullable": bool(null_ok),
                "size":     desc[3],
            })
        return cols

    def get_primary_keys(self, table: str) -> list[str]:
        try:
            pks = [row[3] for row in self.cursor.primaryKeys(table=table)]
            return pks
        except Exception:
            return []

    def get_foreign_keys(self, table: str) -> list[dict]:
        fks = []
        try:
            for row in self.cursor.foreignKeys(foreignTable=table):
                fks.append({
                    "fk_col":    row[7],
                    "ref_table": row[2],
                    "ref_col":   row[3],
                })
        except Exception:
            pass
        return fks

    def get_rows(self, table: str):
        self.cursor.execute(f"SELECT * FROM [{table}]")
        return self.cursor.fetchall()

    def get_column_names(self, table: str) -> list[str]:
        self.cursor.execute(f"SELECT * FROM [{table}] WHERE 1=0")
        return [desc[0] for desc in self.cursor.description]

    def close(self):
        self.conn.close()


class MdbtoolsAccessReader:
    """Lector per a UNIX via mdbtools."""

    _CHARSET_ENVS = [
        {"MDB_JET3_CHARSET": "UTF-8", "MDBICONV": "UTF-8"}, 
        {"MDB_JET3_CHARSET": "CP1252", "MDBICONV": "UTF-8"}, 
        {"MDB_JET3_CHARSET": "CP850",  "MDBICONV": "UTF-8"}, 
        {},  
    ]

    def __init__(self, accdb_path: str):
        import subprocess
        self.path = os.path.abspath(accdb_path)
        self._sp  = subprocess
        self._env = self._detect_env()
        

    # ── Utilitats de baix nivell ──────────────────────────────────────────

    @staticmethod
    def _safe_decode(raw: bytes) -> str:
        """
        Decodifica bytes a str. Prova UTF-8 i UTF-16 amb BOM primer; 
        si falla, usa latin-1.
        """
        if not raw:
            return ""
        if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
            text = raw.decode("utf-16", errors="replace")
            return text.replace("\x00", "")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            pass
        try:
            return raw.decode("cp1252")
        except UnicodeDecodeError:
            pass
        return raw.decode("latin-1", errors="replace")

    def _run(self, cmd: list[str], env_override: dict | None = None) -> bytes:
        """Executa una comanda i retorna stdout com a bytes purs."""
        import os as _os
        env = _os.environ.copy()
        chosen = env_override if env_override is not None else self._env
        env.update(chosen)
        result = self._sp.run(cmd, capture_output=True, env=env)
        return result.stdout

    def _run_str(self, cmd: list[str], env_override: dict | None = None) -> str:
        """Com _run però retorna str decodificat de forma segura."""
        return self._safe_decode(self._run(cmd, env_override))

    def _detect_env(self) -> dict:
        """
        Prova les combinacions de variables d'entorn fins que
        mdb-tables retorna resultats llegibles.
        """
        for env in self._CHARSET_ENVS:
            raw = self._run(["mdb-tables", "-1", self.path], env_override=env)
            if raw:
                text = self._safe_decode(raw)
                if text.strip(): 
                    return env
        return {}
    

    # ── Interfície pública ────────────────────────────────────────────────

    def get_table_names(self) -> list[str]:
        out = self._run_str(["mdb-tables", "-1", self.path])
        return [t.strip() for t in out.splitlines() if t.strip()]

    def get_columns(self, table: str) -> list[dict]:
        out = self._run_str(["mdb-schema", self.path, "-T", table])
        cols = []
        for line in out.splitlines():
            line = line.strip().rstrip(",")
            if line.startswith("[") or line.startswith('"'):
                m = re.match(r'[\["](.+?)[\]"]\s+(\S+.*)', line)
                if m:
                    cols.append({
                        "name":     m.group(1),
                        "type":     m.group(2).upper(),
                        "nullable": True,
                        "size":     None,
                    })
        return cols

    def get_primary_keys(self, table: str) -> list[str]:
        return []

    def get_foreign_keys(self, table: str) -> list[dict]:
        return []

    def get_rows(self, table: str) -> list[tuple]:
        """
        Exporta les dades via mdb-export llegint bytes directament
        per evitar qualsevol UnicodeDecodeError del costat de Python.
        Flags:
          -H  omet la fila de capçalera
          -Q  no posa cometes als camps buits
          -d, delimitador: coma (per defecte)
        """
        import csv, io
        raw = self._run(["mdb-export", "-H", "-Q", self.path, table])
        text = self._safe_decode(raw)
        reader = csv.reader(io.StringIO(text))
        return [tuple(row) for row in reader if any(v.strip() for v in row)]

    def get_column_names(self, table: str) -> list[str]:
        """
        Llegeix només la primera fila (capçalera) de mdb-export.
        """
        import csv, io
        raw = self._run(["mdb-export", self.path, table])
        text = self._safe_decode(raw)
        reader = csv.reader(io.StringIO(text))
        return next(reader, [])

    def close(self):
        pass


# ─── Motor de migració ───────────────────────────────────────────────────────

class AccessToSQLiteMigrator:

    def __init__(self, accdb_path: str, sqlite_path: str, verbose: bool = False):
        self.accdb_path  = accdb_path
        self.sqlite_path = sqlite_path
        self.verbose     = verbose

        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
            level=level,
        )
        self.log = logging.getLogger(__name__)

        connector = get_access_connector()
        self.log.info(f"Connector detectat: {connector}")
        if connector == "pyodbc":
            self.reader = PyodbcAccessReader(accdb_path)
        else:
            self.reader = MdbtoolsAccessReader(accdb_path)

        if os.path.exists(sqlite_path):
            os.remove(sqlite_path)
            self.log.warning(f"S'ha eliminat la base de dades SQLite existent: {sqlite_path}")

        self.sqlite_conn   = sqlite3.connect(sqlite_path)
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.sqlite_cursor.execute("PRAGMA foreign_keys = ON;")
        self.sqlite_cursor.execute("PRAGMA journal_mode = WAL;")


    # ── Creació d'esquema ──────────────────────────────────────────────────

    def _create_table_ddl(self, table: str) -> str:
        columns  = self.reader.get_columns(table)
        pks      = self.reader.get_primary_keys(table)
        fks      = self.reader.get_foreign_keys(table)

        col_defs = []
        for col in columns:
            sq_type = map_type(col["type"])
            null_kw = "" if col["nullable"] else " NOT NULL"
            pk_kw   = " PRIMARY KEY" if col["name"] in pks and len(pks) == 1 else ""
            col_defs.append(f'    "{col["name"]}" {sq_type}{null_kw}{pk_kw}')

        if len(pks) > 1:
            pk_cols = ", ".join(f'"{c}"' for c in pks)
            col_defs.append(f"    PRIMARY KEY ({pk_cols})")

        for fk in fks:
            col_defs.append(
                f'    FOREIGN KEY ("{fk["fk_col"]}")'
                f' REFERENCES "{fk["ref_table"]}" ("{fk["ref_col"]}")'
            )

        body = ",\n".join(col_defs)
        return f'CREATE TABLE IF NOT EXISTS "{table}" (\n{body}\n);'
    

    # ── Migració d'una taula ───────────────────────────────────────────────

    def _migrate_table(self, table: str):
        ddl = self._create_table_ddl(table)
        self.log.debug(f"DDL:\n{ddl}")
        self.sqlite_cursor.execute(ddl)

        col_names = self.reader.get_column_names(table)
        rows      = self.reader.get_rows(table)

        if not rows:
            self.log.info(f"  Taula '{table}': buida (0 files)")
            return

        placeholders = ", ".join("?" * len(col_names))
        cols_quoted  = ", ".join(f'"{c}"' for c in col_names)
        insert_sql   = f'INSERT OR IGNORE INTO "{table}" ({cols_quoted}) VALUES ({placeholders})'

        def sanitize(row) -> tuple:
            import decimal
            result = []
            for v in row:
                if isinstance(v, bool):
                    result.append(int(v))
                elif hasattr(v, "isoformat"): 
                    result.append(v.isoformat())
                elif isinstance(v, decimal.Decimal):
                    result.append(float(v))
                elif isinstance(v, (bytes, bytearray)):
                    result.append(sqlite3.Binary(v))
                else:
                    result.append(v)
            return tuple(result)

        sanitized = [sanitize(r) for r in rows]
        self.sqlite_cursor.executemany(insert_sql, sanitized)
        self.log.info(f"  Taula '{table}': {len(sanitized)} files migrades")


    # ── Punt d'entrada principal ───────────────────────────────────────────

    def migrate(self):
        tables = self.reader.get_table_names()
        self.log.info(f"Taules trobades: {len(tables)} → {tables}")

        self.log.info("Pas 1/3 – Creant esquema (sense claus foranes)…")
        for table in tables:
            columns = self.reader.get_columns(table)
            pks     = self.reader.get_primary_keys(table)
            col_defs = []
            for col in columns:
                sq_type = map_type(col["type"])
                null_kw = "" if col["nullable"] else " NOT NULL"
                pk_kw   = " PRIMARY KEY" if col["name"] in pks and len(pks) == 1 else ""
                col_defs.append(f'    "{col["name"]}" {sq_type}{null_kw}{pk_kw}')
            if len(pks) > 1:
                pk_cols = ", ".join(f'"{c}"' for c in pks)
                col_defs.append(f"    PRIMARY KEY ({pk_cols})")
            body = ",\n".join(col_defs)
            ddl  = f'CREATE TABLE IF NOT EXISTS "{table}" (\n{body}\n);'
            self.log.debug(f"DDL (sense FK): {table}\n{ddl}")
            self.sqlite_cursor.execute(ddl)
        self.sqlite_conn.commit()

        self.log.info("Pas 2/3 – Migrant dades…")
        for table in tables:
            col_names = self.reader.get_column_names(table)
            rows      = self.reader.get_rows(table)
            if not rows:
                self.log.info(f"  Taula '{table}': buida")
                continue
            placeholders = ", ".join("?" * len(col_names))
            cols_quoted  = ", ".join(f'"{c}"' for c in col_names)
            insert_sql   = f'INSERT OR IGNORE INTO "{table}" ({cols_quoted}) VALUES ({placeholders})'

            def sanitize(row: Any) -> tuple:
                import decimal
                result = []
                for v in row:
                    if isinstance(v, bool):
                        result.append(int(v))
                    elif hasattr(v, "isoformat"): 
                        result.append(v.isoformat())
                    elif isinstance(v, decimal.Decimal):
                        result.append(float(v))
                    elif isinstance(v, (bytes, bytearray)):
                        result.append(sqlite3.Binary(v))
                    else:
                        result.append(v)
                return tuple(result)

            sanitized = [sanitize(r) for r in rows]
            try:
                self.sqlite_cursor.executemany(insert_sql, sanitized)
                self.log.info(f"  '{table}': {len(sanitized)} files")
            except sqlite3.Error as e:
                self.log.error(f"  Error a '{table}': {e}")
        self.sqlite_conn.commit()

        self.log.info("Pas 3/3 – Aplicant claus foranes…")
        fk_added = 0
        for table in tables:
            fks = self.reader.get_foreign_keys(table)
            if not fks:
                continue
            self.log.debug(f"  FK a '{table}': {fks}")
            fk_added += len(fks)
            self._rebuild_table_with_fk(table)
        if fk_added == 0:
            self.log.info("  Cap clau forana trobada (pot ser normal segons el connector).")
        self.sqlite_conn.commit()

        self.log.info("✓ Migració completada!")
        self._print_summary(tables)

    def _rebuild_table_with_fk(self, table: str):
        """
        SQLite no permet ALTER TABLE ADD FOREIGN KEY.
        Tècnica oficial: crear taula temporal → copiar dades → eliminar original → renombrar.
        """
        ddl_with_fk = self._create_table_ddl(table)
        tmp = f"__tmp_{table}"
        ddl_tmp = ddl_with_fk.replace(
            f'CREATE TABLE IF NOT EXISTS "{table}"',
            f'CREATE TABLE "{tmp}"'
        )
        try:
            self.sqlite_cursor.execute(ddl_tmp)
            self.sqlite_cursor.execute(f'INSERT INTO "{tmp}" SELECT * FROM "{table}"')
            self.sqlite_cursor.execute(f'DROP TABLE "{table}"')
            self.sqlite_cursor.execute(f'ALTER TABLE "{tmp}" RENAME TO "{table}"')
            self.log.debug(f"  Taula '{table}' reconstruïda amb FK.")
        except sqlite3.Error as e:
            self.log.warning(f"  No s'ha pogut reconstruir '{table}' amb FK: {e}")
            try:
                self.sqlite_cursor.execute(f'DROP TABLE IF EXISTS "{tmp}"')
            except Exception:
                pass

    def _print_summary(self, tables: list[str]):
        print("\n" + "═" * 50)
        print("  RESUM DE LA MIGRACIÓ")
        print("═" * 50)
        for table in tables:
            self.sqlite_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = self.sqlite_cursor.fetchone()[0]
            print(f"  {table:<35} {count:>8} files")
        print("═" * 50)
        size_kb = os.path.getsize(self.sqlite_path) // 1024
        print(f"  Arxiu SQLite: {self.sqlite_path}  ({size_kb} KB)")
        print("═" * 50 + "\n")

    def close(self):
        self.reader.close()
        self.sqlite_conn.close()


# ─── Línia de Comandes ─────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Migra una base de dades Access (.accdb/.mdb) a SQLite."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        metavar="ARXIU.accdb",
        help="Ruta a l'arxiu Access d'origen",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        metavar="ARXIU.sqlite",
        help="Ruta de la base de dades SQLite de destinació (es crearà de nou)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mostra informació detallada de depuració",
    )
    return parser.parse_args()


# ─── MAIN ──────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: no s'ha trobat l'arxiu '{args.input}'", file=sys.stderr)
        sys.exit(1)

    migrator = AccessToSQLiteMigrator(
        accdb_path  = args.input,
        sqlite_path = args.output,
        verbose     = args.verbose,
    )
    try:
        migrator.migrate()
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
