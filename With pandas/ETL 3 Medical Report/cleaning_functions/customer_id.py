import pandas as pd

def clean_customer_id(df: pd.DataFrame) -> pd.DataFrame:
    try:
        numbers_only = (df['customer_id']
                        .str.strip()
                        .str.replace(r'\D', '',regex=True)
                        .str.replace(' ', '')
                        )

        df = df[numbers_only.str.len() == 4 ]
        
        df['customer_id'] = df['customer_id'].fillna('uknown')
  
        return df
    except Exception as e:
        print(f"Error in clean_customer_id: {e}")
        return None
