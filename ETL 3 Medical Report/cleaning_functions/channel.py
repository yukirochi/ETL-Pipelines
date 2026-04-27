import pandas as pd
from cleaning_tools.match_spelling import match_spelling

def clean_channel(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df['channel'] = df['channel'].str.strip().str.title()

        # Pass DataFrame, column name (string), and unique values
        df = match_spelling(df, 'channel')
        
        return df
    except Exception as e:
        print(f"Error in clean_channel: {e}")
        return None
        
    #solve the error 
