import pandas as pd
from thefuzz import fuzz

def find_best_match(values: pd.DataFrame) -> pd.DataFrame: #finding unique right spelled values in column
    try:
        counts = values.value_counts()
        unique_values = counts[counts >= 3].index.tolist()
        return unique_values
    except Exception as e:
        print(f"Error in find_best_match: {e}")
        return []

def match_spelling(df: pd.DataFrame, col_name,unique_values: list) -> pd.DataFrame:
    try:
        col = df[col_name]
        for value in col.unique():
            if value not in unique_values:
                best_match = max(unique_values, key=lambda x: fuzz.ratio(value, x))

                if  fuzz.ratio(value, best_match) >= 75:
                    # (col == value) = boolean checklist showing which ROWS match (DOWN direction)
                    # col_name = which COLUMN to update (RIGHT direction)
                    # Together they create the exact coordinate to update
                    df.loc[col == value, col_name] = best_match
                else:
                    # Same logic: find matching rows, update only in this column
                    df.loc[col == value, col_name] = 'unknown'
    except Exception as e:
        print(f"Error in match_spelling: {e}")
