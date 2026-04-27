import pandas as pd
import sqlite3
from thefuzz import fuzz
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "medical report.csv"

def read_csv(path: Path) -> pd.DataFrame:
    try:
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
    except Exception as e:
        print(f"Error in read_csv: {e}")
        return None