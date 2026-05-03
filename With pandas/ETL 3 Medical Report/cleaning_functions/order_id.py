import pandas as pd

def clean_order_id(df: pd.DataFrame) -> pd.DataFrame:   
    try:
        df.drop_duplicates(subset=['order_id'], inplace=True)
        
        clean_id = (df["order_id"]
                          .str.strip()
                          .str.replace('MD', '')
                          .str.replace('-', '')
                          .str.replace(r'\D', '', regex=True))
        
        df = df[clean_id.str.len() == 9]
        
        return df
    except Exception as e:
        print(f"Error in clean_order_id: {e}")
        return None
