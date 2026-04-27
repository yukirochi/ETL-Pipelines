import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_product_name(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = match_spelling(df, 'product_name', 2)

        return df
    except Exception as e:
        print(f"Error in clean_product_name: {e}")
        return None