import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_status(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['status'] = df['status'].str.strip().str.title()
        df = match_spelling(df, 'status', 2)
        return df
    except Exception as e:
        print(f"Error in clean_status: {e}")
        return None 