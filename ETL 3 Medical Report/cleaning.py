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

    regions = ["North", 
               "South", 
               "East", 
               "West", 
               "Central",
               'Northwest', 
               'Southeast', 
               'Northeast', 
               'Southwest',
               'midwest']
    
    for region in df['region'].unique():
        if region not in regions:
            # Find best matching region by similarity score. E.g., "Nort" matches "North" with ~89% similarity
            best_match = max(regions, key=lambda r: fuzz.ratio(region, r)) 
            #max return the highest value ex max(2, 3) returns 3 
            # then this uses a lamba function to calculate the similarity score between the region and each of the 
            # valid regions, and returns the region with the highest score as the best match.
            if fuzz.ratio(region, best_match) >= 80:
                df.loc[df['region'] == region, 'region'] = best_match
            else:
                df.loc[df['region'] == region, 'region'] = 'Unknown'
    
    df['region'] = df['region'].str.strip().str.title()
    df['region'] = df['region'].apply(lambda x: 'Unknown' if pd.isna(x) else x)
    return df


def clean_channel(df: pd.DataFrame) -> pd.DataFrame:
    df['Channel'] = df['Channel'].apply(lambda x: 'unknown')
    #appy fuzzing return unique values from the dataframe instead of listing it 

df = read_csv(CSV_PATH)

df = clean_order_id(df)

df = clean_invoice_id(df)

df = clean_dates(df)

df = clean_region(df)

print(df.head(10))
print(len(df)) #original length is 299

