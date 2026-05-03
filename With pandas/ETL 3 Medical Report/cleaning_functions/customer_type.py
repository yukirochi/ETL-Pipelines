import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_customer_type(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['customer_type'] = df['customer_type'].str.strip().str.title()

        df = match_spelling(df, 'customer_type')

        return df
    except Exception as e:
        print(f"Error in clean_customer_type: {e}")
        return None
