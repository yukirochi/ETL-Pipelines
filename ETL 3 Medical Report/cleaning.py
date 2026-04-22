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

def find_best_match(values: pd.DataFrame) -> pd.DataFrame: #finding unique right spelled values in column
    counts = values.value_counts()
    unique_values = counts[counts >= 3].index.tolist()
    return unique_values

def match_spelling(col: pd.DataFrame, unique_values: list) -> pd.DataFrame:
    for value in col.unique():
        if value not in unique_values:
            best_match = max(unique_values, key=lambda x: fuzz.ratio(value, x))

            if  fuzz.ratio(value, best_match) >= 75:
                df.loc[col == value, col] = best_match
            else:
                df.loc[col == value, col] = 'unknown'

def clean_region(df: pd.DataFrame) -> pd.DataFrame:

    df['region'] = df['region'].str.strip().str.title()
    regions = find_best_match(df['region'])
    
    match_spelling(df['region'], regions)

    df['region'] = df['region'].apply(lambda x: 'Unknown' if pd.isna(x) else x)
    return df


def clean_channel(df: pd.DataFrame) -> pd.DataFrame:
    df['channel'] = df['channel'].str.strip().str.title()
    
    channels = find_best_match(df['channel'])

    match_spelling(df['channel'], channels)
    
    return df
        
    #solve the error 

df = read_csv(CSV_PATH)

df = clean_order_id(df)

df = clean_invoice_id(df)

df = clean_dates(df)

df = clean_region(df)

df = clean_channel(df)

print(df.head(20))
print(len(df)) #original length is 299

