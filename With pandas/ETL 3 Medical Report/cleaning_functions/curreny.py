import pandas as pd
from cleaning_tools.match_spelling import match_spelling
def clean_currency(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['currency'] = df['currency'].str.strip().str.upper()
        df = match_spelling(df, 'currency')
        return df
    except Exception as e:
        print(f"Error in clean_currency: {e}")
        return None