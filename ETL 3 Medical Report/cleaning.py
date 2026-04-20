import pandas as pd
import sqlite3
from thefuzz import fuzz
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "medical report.csv"

def read_csv(path: Path) -> pd.DataFrame:

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")  
    
    df = pd.read_csv(path)
    
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        )
    
    return df

def clean_order_id(df: pd.DataFrame) -> pd.DataFrame:   
    df.drop_duplicates(subset=['order_id'], inplace=True)
    
    clean_id = (df["order_id"]
                      .str.strip()
                      .str.replace('MD', '')
                      .str.replace('-', '')
                      .str.replace(r'\D', '', regex=True))
    
    df = df[clean_id.str.len() == 9]
    return df

def clean_invoice_id(df: pd.DataFrame) -> pd.DataFrame:
    df.drop_duplicates(subset=['invoice_id'], inplace=True)
    
    clean_id = (df["invoice_id"]
                      .str.strip()
                      .str.replace('INV', '')
                      .str.replace('-', '')
                      .str.replace(r'\D', '', regex=True))
    
    df = df[clean_id.str.len() == 6]
    return df

def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    
    for col in ("order_date", "ship_date", 'delivery_date'):
        normalized_col = df[col].str.strip().str.replace(r'[ /]', '-', regex=True)
        df[col] = pd.to_datetime(normalized_col,format='mixed', errors='coerce').dt.date
        df[col] = df[col].apply(lambda x: 'unknown' if pd.isna(str(x)) else x )

    df = df[~(df['ship_date'] < df['order_date'])]
    df = df[~(df['delivery_date'] < df['ship_date'])]
    return df

def clean_region(df: pd.DataFrame) -> pd.DataFrame:

    return df

df = read_csv(CSV_PATH)

df = clean_order_id(df)

df = clean_invoice_id(df)

df = clean_dates(df)

print(df.head(10))
print(len(df)) #original length is 299

