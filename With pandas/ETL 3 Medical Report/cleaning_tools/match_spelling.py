import pandas as pd
from thefuzz import fuzz
from cleaning_tools.find_unique_values import find_unique_values 

def match_spelling(df: pd.DataFrame, col_name: str, count: int = 3) -> pd.DataFrame:
    try:
        col = df[col_name]
        unique_values = find_unique_values(col, count)
        
        if not unique_values:
            print(f'no unique values found that appear {count} times or more')
            return df
        
        without_nan_values  = [v for v in df[col_name].unique() if pd.notna(v)]
        
        for value in without_nan_values:
            if str(value) in unique_values:
                continue

            best_match = max(unique_values, key=lambda x: fuzz.ratio(value, x))

            if  fuzz.ratio(value, best_match) >= 75:
                    # (col == value) = boolean checklist showing which ROWS match (DOWN direction)
                    # col_name = which COLUMN to update (RIGHT direction)
                    # Together they create the exact coordinate to update
                equivalent =  best_match.title()
            else:
                    # Same logic: find matching rows, update only in this column
                equivalent = 'unknown'

            df.loc[col == value, col_name] = equivalent
        df[col_name] = df[col_name].fillna('unknown')  #fill the NaN values with 'unknown' after the matching process
    except Exception as e:
        print(f"Error in match_spelling: {e}")

    return df