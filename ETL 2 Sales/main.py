import pandas as pd
import sqlite3
import numpy as np
import pycountry_convert as pc
df = pd.read_csv("sales_report.csv")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

df.drop_duplicates(subset=['order_id'], inplace=True)
df['order_id'] = (df["order_id"].str.strip()
                  .str.replace(' ', '')
                  .str.replace('-', '')
                  .astype(str)
                  .str.replace(r'\D', '', regex=True) #remove non digit characters
                  )
                 
df['order_id'] = df['order_id'].where( #condition if its a right value to modify, if not then replace it with N/A
                      (df['order_id'].astype(str).str.len() == 6) & df['order_id'].notna(), 'N/A') 
                  

df['order_date'] = df['order_date'].str.strip().str.replace(' ', '-').str.replace('/', '-', regex=True)
df['order_date'] = pd.to_datetime(df['order_date'],format='mixed', errors='coerce').dt.date #.dt.date remove the time part and keep only the date

df['ship_date'] = df['ship_date'].str.strip().str.replace(' ', '-').str.replace('/', '-', regex=True)
df['ship_date'] = pd.to_datetime(df['ship_date'],format='mixed', errors='coerce').dt.date

df = df[~(df['ship_date'] < df['order_date'])] # ~ is the negation operator, it means we want to keep the rows where ship_date is not less than order_date

df['customer_name'] = df['customer_name'].str.strip().str.title()

df['customer_email'] = df['customer_email'].str.strip().str.lower().str.replace(' ', '')
df['customer_email'] = df['customer_email'].where(df['customer_email'].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', regex=True), 'invalid@gmail.com') #if the email is not valid, replace it with


def find_region(country):
    try:
        country_code = pc.country_name_to_country_alpha2(country) #convert country name to country code, for example: United States -> US
        continent_code = pc.country_alpha2_to_continent_code(country_code) #convert country code to continent code, for example: US -> NA (North America)
        return continent_code
    except:
        return 'Unknown'
    
df['region'] = df['country'].apply(lambda x: find_region(x))

df['discount'] = df['discount'].fillna(0) #replace null values with 0
df['discount'] = df['discount'].str.strip().where(df['discount'].str.endswith('%'), df['discount'].str.rstrip('%').astype(float) * 100)
df['discount'] = df['discount'].apply(lambda x: str(x) + '%' if isinstance(x, (int, float)) else x)

print(df.head()) 
print(len(df)) 