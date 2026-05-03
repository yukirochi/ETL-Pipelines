import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_payment_method(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['payment_method'] = df['payment_method'].str.strip().str.title()
        df = match_spelling(df, 'payment_method', 2)
        return df
    except Exception as e:
        print(f"Error in clean_payment_method: {e}")
        return None