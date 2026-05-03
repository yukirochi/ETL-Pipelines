import pandas as pd

def verify_sales(df: pd.DataFrame) -> pd.DataFrame:
    try:
        quantity = df['quantity'] 
        unit_price = df['unit_price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
        discount_pct = df['discount_pct'].str.replace(r'[^\d.]', '', regex=True).astype(float) / 100
        tax_pct = df['tax_pct'].str.replace(r'[^\d.]', '', regex=True).astype(float) / 100
        sales_amount = df['sales_amount'].str.replace(r'[^\d.]', '', regex=True).astype(float)
        cogs = df['cogs'].str.replace(r'[^\d.]', '', regex=True).astype(float)
        profit = df['profit'].str.replace(r'[^\d.]', '', regex=True).astype(float)

        calculated_sales_amount = quantity * unit_price * (1 - discount_pct) * (1 + tax_pct)
        calculated_profit = calculated_sales_amount - cogs

        sales_diff = abs(calculated_sales_amount - sales_amount)
        profit_diff = abs(calculated_profit - profit)
        
        df = df[ (sales_diff <= 0.1) & (profit_diff <= 0.1) ]
        return df
    except Exception as e:
        print(f"Error occurred while verifying sales_amount column: {e}")
        return None