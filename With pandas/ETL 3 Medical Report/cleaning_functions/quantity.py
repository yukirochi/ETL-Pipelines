import pandas as pd

def clean_quantity(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).round(0).astype(int).abs()
      
        return df
    except Exception as e:
        print(f"Error occurred while cleaning quantity column: {e}")
        return None