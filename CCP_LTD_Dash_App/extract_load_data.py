# pip install supabase

import os
import io
import zipfile
import requests
import sqlite3
from supabase import create_client, Client

# for GitHub:
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


SUPABASE_URL = "https://jcobxvpdygzzmakkamoy.supabase.co"
SUPABASE_KEY_service_role = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impjb2J4dnBkeWd6em1ha2thbW95Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDAxMDk4NCwiZXhwIjoyMDc1NTg2OTg0fQ.O4ZfK_UaVvF0e4SaNsuuq4AmCsptEGODKuPF4dKKqSI"
output_dir = "./data"

def download_and_extract_zip(url, output_dir="."):
    """Скачивает ZIP по URL, распаковывает и возвращает путь к SQLite файлу"""
    try:
        r = requests.get(url)
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(output_dir)

        sqlite_path = os.path.join(output_dir, "results", "filings_demo_step3.sqlite")
        return sqlite_path

    except Exception as e:
        print(f"Error during download or extraction: {e}")
        raise


def get_table_names(sqlite_path):
    """Возвращает список таблиц из базы"""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables


def upload_sqlite_to_supabase(sqlite_path, supabase: Client):
    """Выгружает все таблицы из SQLite и записывает их в Supabase"""
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tables = get_table_names(sqlite_path)
    # print(f"Tables found: {tables}\n")

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        if not rows:
            print(f"Table {table} is empty, skipping.")
            continue

        # print(f"Uploading {len(rows)} rows to table '{table}'...")

        try:
            # Отправляем данные в Supabase
            response = supabase.table(table).upsert(rows).execute()
            # print(f"Table '{table}' successfully uploaded ({len(rows)} records).")
        except Exception as e:
            print(f"Error uploading table {table}: {e}")

    conn.close()
    # print("All data has been uploaded to Supabase.")


if __name__ == "__main__":
    # Подключаемся к Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY_service_role)
    # Ссылка на ZIP
    url = "https://raw.githubusercontent.com/ronihogri/financial-doc-reader/main/steps/step3_extract_by_concept/results.zip"

    # 1️⃣ Скачать и распаковать архив
    sqlite_file = download_and_extract_zip(url, output_dir)

    # 2️⃣ Выгрузить все таблицы из SQLite прямо в Supabase
    upload_sqlite_to_supabase(sqlite_file, supabase)