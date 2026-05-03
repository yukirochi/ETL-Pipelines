import pandas as pd
from thefuzz import fuzz

def find_unique_values(column: pd.Series, count: int) -> list: #finding unique right spelled values in column
    try:
        counts = column.value_counts(dropna=True)
        unique_values = [str(v) for v in counts[counts >= count].index if pd.notna(v)]
        return unique_values
    except Exception as e:
        print(f"Error in find_best_match: {e}")
        return []
