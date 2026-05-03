import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_product_category(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['product_category'] = df['product_category'].str.strip().str.title()

        df = match_spelling(df, 'product_category')

        return df
    except Exception as e:
        print(f"Error in clean_product_category: {e}")
        return None