import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_region(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['region'] = df['region'].str.strip().str.title()

        df = match_spelling(df, 'region')

        df['region'] = df['region'].apply(lambda x: 'Unknown' if pd.isna(x) else x)
        return df
    except Exception as e:
        print(f"Error in clean_region: {e}")
        return None
