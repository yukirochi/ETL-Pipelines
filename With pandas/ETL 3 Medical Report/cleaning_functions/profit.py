import pandas as pd

def clean_profit(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['profit'] = df['profit'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0).round(2).abs()
        df['profit'] = df['profit'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
        return df
    except Exception as e:
        print(f"Error occurred while cleaning profit column: {e}")
        return None