# pip install supabase

from supabase import create_client, Client
import pandas as pd

# for GitHub:
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_&&&&&")

SUPABASE_URL = "https://jcobxvpdygzzmakkamoy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impjb2J4dnBkeWd6em1ha2thbW95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwMTA5ODQsImV4cCI6MjA3NTU4Njk4NH0.ny-fRFJ8b4QFPe7KLBpOBVX5D5_vWjVqJCuiI94ucVk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

forms = supabase.table("Forms").select("id, CIK, ValueDate, FilingDate").execute()
tasks = supabase.table("Tasks").select("Form_id, CCP, LTD").execute()
stocks = supabase.table("Stocks").select("CIK, Symbol, CompanyName").execute()

df_forms = pd.DataFrame(forms.data)
df_tasks = pd.DataFrame(tasks.data)
df_stocks = pd.DataFrame(stocks.data)

result_df = df_forms.merge(df_tasks, left_on="id", right_on="Form_id", how="left").merge(df_stocks, on="CIK", how="left")

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
