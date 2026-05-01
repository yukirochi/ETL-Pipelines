import pandas as pd


def clean_cogs(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['cogs'] = df['cogs'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df['cogs'] = pd.to_numeric(df['cogs'], errors='coerce').fillna(0).round(2).abs()
        df['cogs'] = df['cogs'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00")
        return df
    except Exception as e:
        print(f"Error occurred while cleaning cogs column: {e}")
        return None