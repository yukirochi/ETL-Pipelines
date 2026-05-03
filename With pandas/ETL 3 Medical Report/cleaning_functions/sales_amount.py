import pandas as pd

def clean_sales_amount(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['sales_amount'] = df['sales_amount'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce').fillna(0).round(2).abs()
        df['sales_amount'] = df['sales_amount'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
        return df
    except Exception as e:
        print(f"Error occurred while cleaning sales_amount column: {e}")
        return None