import pandas as pd

def clean_tax_pct(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['tax_pct'] = df['tax_pct'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['tax_pct'] = pd.to_numeric(df['tax_pct'], errors='coerce').fillna(0).round(2).abs()
        df['tax_pct'] = [str(int(x * 100)) + '%' for x in df['tax_pct']]
        return df
    except Exception as e:
        print(f"Error occurred while cleaning tax_pct column: {e}")
        return None