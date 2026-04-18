import pandas as pd
import sqlite3
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

    return df


df = read_csv(CSV_PATH)
print(df.head())
df = clean_order_id(df)

