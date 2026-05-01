import pandas as pd

def clean_discount_pct(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['discount_pct'] = pd.to_numeric(df['discount_pct'], errors='coerce').fillna(0).round(2).abs()
        df['discount_pct'] = [str(int(x * 100)) + '%' for x in df['discount_pct']]
        return df
    except Exception as e:
        print(f"Error occurred while cleaning discount_pct column: {e}")
        return None