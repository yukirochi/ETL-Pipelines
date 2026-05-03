import pandas as pd

def clean_invoice_id(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df.drop_duplicates(subset=['invoice_id'], inplace=True)
        
        clean_id = (df["invoice_id"]
                          .str.strip()
                          .str.replace('INV', '')
                          .str.replace('-', '')
                          .str.replace(r'\D', '', regex=True))
        
        df = df[clean_id.str.len() == 6]
        return df
    except Exception as e:
        print(f"Error in clean_invoice_id: {e}")
        return None
