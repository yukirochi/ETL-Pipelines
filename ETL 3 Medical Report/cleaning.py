from dbm import error

import pandas as pd
import sqlite3
from thefuzz import fuzz
from pathlib import Path
from functions import find_best_match, match_spelling

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

    df['region'] = df['region'].str.strip().str.title()

    df = match_spelling(df, 'region')

    df['region'] = df['region'].apply(lambda x: 'Unknown' if pd.isna(x) else x)
    return df


def clean_channel(df: pd.DataFrame) -> pd.DataFrame:
    df['channel'] = df['channel'].str.strip().str.title()

    # Pass DataFrame, column name (string), and unique values
    df = match_spelling(df, 'channel')
    
    return df
        
    #solve the error 

def clean_customer_type(df: pd.DataFrame) -> pd.DataFrame:
    df['customer_type'] = df['customer_type'].str.strip().str.title()

    df = match_spelling(df, 'customer_type')

    return df

df = read_csv(CSV_PATH)

df = clean_order_id(df)

df = clean_invoice_id(df)

df = clean_dates(df)

df = clean_region(df)

df = clean_channel(df)

df  = clean_customer_type(df)

print(df['customer_type'].head(30))
# print(df.head())
print(len(df)) #original length is 299



