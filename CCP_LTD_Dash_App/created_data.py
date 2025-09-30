# pip install numpy pandas plotly requests

import io
import os
import numpy as np
import pandas as pd
import sqlite3
import zipfile

import requests

def download_and_extract_zip(url, output_dir="."):
    try:
        r = requests.get(url)
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(output_dir)

        sqlite_path = os.path.join(output_dir, "results", "filings_demo_step3.sqlite")
        return sqlite_path

    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        raise
    except zipfile.BadZipFile:
        print("Error: Downloaded file is not a valid zip file")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


url = url
sqlite_path = download_and_extract_zip(url)

def create_merged_dataframe(sqlite_path):
    try:
        conn = sqlite3.connect(sqlite_path)

        df_tasks = pd.read_sql_query("SELECT * FROM Tasks", conn)
        df_stocks = pd.read_sql_query("SELECT * FROM Stocks", conn)
        df_forms = pd.read_sql_query("SELECT * FROM Forms", conn)

        conn.close()

        final_merged = df_tasks.merge(df_forms, left_on="Form_id", right_on="id").merge(df_stocks, on="CIK", how="inner")

        return final_merged

    except sqlite3.Error as e:
        print(f"Error when working with SQLite: {e}")
        return None
    except Exception as e:
        print(f"An error has occurred unrelated to SQLite: {e}")
        return None


result_df = create_merged_dataframe(sqlite_path)


result_df['ValueDate'] = pd.to_datetime(result_df['ValueDate'], errors='coerce')
result_df['FilingDate'] = pd.to_datetime(result_df['FilingDate'], errors='coerce')

def normalize_date(date):
    if pd.isna(date):
        return pd.NaT
    month = date.month
    year = date.year
    if month in [1, 2, 3]:
        return pd.Timestamp(year=year-1, month=12, day=31)
    elif month in [4, 5, 6]:
        return pd.Timestamp(year=year, month=3, day=31)
    elif month in [7, 8, 9]:
        return pd.Timestamp(year=year, month=6, day=30)
    elif month in [10, 11, 12]:
        return pd.Timestamp(year=year, month=9, day=30)
    else:
        return pd.NaT

result_df['NormalizedQuarter'] = result_df['FilingDate'].apply(normalize_date)
result_df['NormalizedQuarter'] = pd.to_datetime(result_df['NormalizedQuarter'], errors='coerce')
result_df['Ratio_CCP_LTD'] = round(result_df['CCP'] / result_df['LTD'], 4)

# print(result_df.head())



