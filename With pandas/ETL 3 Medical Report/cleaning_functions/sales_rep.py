import pandas as pd
from cleaning_tools.match_spelling import match_spelling
def clean_sales_rep(df : pd.DataFrame) -> pd.DataFrame:
    try:
        df['sales_rep'] = df['sales_rep'].str.strip().str.title()
        df = match_spelling(df, 'sales_rep', 2)
        return df
    except Exception as e:
        print(f"Error in clean_sales_rep: {e}")
        return None