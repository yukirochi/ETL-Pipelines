import pandas as pd

def clean_unit_price(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['unit_price'] = df['unit_price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0).round(2).abs()
        df['unit_price'] = df['unit_price'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
        return df
    except Exception as e:
        print(f"Error occurred while cleaning unit_price column: {e}")
        return None