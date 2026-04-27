import pandas as pd

def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    try:
        for col in ("order_date", "ship_date", 'delivery_date'):
            normalized_col = df[col].str.strip().str.replace(r'[ /]', '-', regex=True)
            df[col] = pd.to_datetime(normalized_col,format='mixed', errors='coerce').dt.date
            df[col] = df[col].apply(lambda x: 'unknown' if pd.isna(str(x)) else x )

        df = df[~(df['ship_date'] < df['order_date'])]
        df = df[~(df['delivery_date'] < df['ship_date'])]
        return df
    except Exception as e:
        print(f"Error in clean_dates: {e}")
        return None
