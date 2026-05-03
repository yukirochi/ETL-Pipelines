import pandas as pd
import sqlite3
import numpy as np
import pycountry_convert as pc
import os
df = pd.read_csv("sales_report.csv")

maindir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(maindir, "sales.db")

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
df['discount'] = df['discount'].str.replace('%', '').astype(float).round(2).astype(str) + '%' #remove % and convert to float and round to 2 decimal places and add % back

df = df[~(df['sales_amount'].astype(str).str.contains('-'))] #remove rows where sales_amount contains negative values
df['sales_amount'] = df['sales_amount'].apply(lambda x: '$'+ str(x) if '$' not in str(x) else x)
df['sales_amount'] = df['sales_amount'].str.replace(',','').str.strip() #remove commas and strip spaces
df['sales_amount'] = df['sales_amount'].str.replace('$','').astype(float).round(2) #remove $ and convert to float and round to 2 decimal places
df['sales_amount'] = df['sales_amount'].apply(lambda x: '${:,.2f}'.format(x)) #format sales_amount to have $ and 2 decimal places

df['payment_method'] = df['payment_method'].str.title()

df['salesperson'] = df['salesperson'].str.strip().str.title().str.replace(' ', '')
df['channel'] = df['channel'].str.title()
df['status'] = df['status'].str.title()

df['quantity'] = df['quantity'].apply(lambda x: int(x) if str(x).isdigit() else np.nan) #convert quantity to integer, if it cannot be converted then replace it with NaN
df = df[df['quantity'].astype(float) > 0] #remove rows where quantity is less than or equal to 0

df['unit_price'] = df['unit_price'].str.replace('$','').str.replace(',','').astype(float).round(2) #remove $ and commas and convert to float and round to 2 decimal places
df['unit_price'] = df['unit_price'].apply(lambda x: '${:,.2f}'.format(x)) #format unit_price to have $ and 2 decimal places

df = df[ df['quantity'].astype(str).str.replace('$','').astype(float) > 0 & df['sales_amount'].notna()]#remove rows where quantity is less than or equal to 0 and sales_amount is null
df = df.drop(columns=['row_id']) 

connection = sqlite3.connect(db_path)
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
    order_id TEXT,
    order_date TEXT,
    ship_date TEXT,
    customer_name TEXT,
    customer_email TEXT,
    region TEXT,
    country TEXT,
    product TEXT,
    category TEXT,
    quantity INTEGER,
    unit_price TEXT,
    discount TEXT,
    sales_amount TEXT,
    payment_method TEXT,
    salesperson TEXT,
    channel TEXT,
    status TEXT,
    notes TEXT
)
''')

df.to_sql('sales', connection, if_exists='append', index=False)


print(df.head(1)) #print the first row of the dataframe to check if the data is cleaned properly
print(len(df)) 