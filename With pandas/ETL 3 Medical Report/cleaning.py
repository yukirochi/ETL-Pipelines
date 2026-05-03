from dbm import error

import pandas as pd
import sqlite3
from thefuzz import fuzz
from pathlib import Path
from cleaning_functions.read_csv import read_csv
from cleaning_functions.channel import clean_channel
from cleaning_functions.customer_type import clean_customer_type
from cleaning_functions.region import clean_region
from cleaning_functions.dates import clean_dates
from cleaning_functions.invoice_id import clean_invoice_id
from cleaning_functions.order_id import clean_order_id
from cleaning_functions.customer_id import clean_customer_id
from cleaning_functions.sales_rep import clean_sales_rep
from cleaning_functions.product_name import clean_product_name
from cleaning_functions.product_category import clean_product_category
from cleaning_functions.quantity import clean_quantity
from cleaning_functions.unit_price import clean_unit_price
from cleaning_functions.discount_pct import clean_discount_pct
from cleaning_functions.tax_pct import clean_tax_pct
from cleaning_functions.sales_amount import clean_sales_amount
from cleaning_functions.profit import clean_profit
from cleaning_functions.cogs import clean_cogs
from cleaning_functions.verify_sales import verify_sales
from cleaning_functions.curreny import clean_currency
from cleaning_functions.payment_method import clean_payment_method
from cleaning_functions.status import clean_status
from sql import connection
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "medical report.csv"



df = read_csv(CSV_PATH)

df = clean_order_id(df)

df = clean_invoice_id(df)

df = clean_dates(df)

df = clean_region(df)

df = clean_channel(df)

df  = clean_customer_type(df)

df = clean_customer_id(df)

df = clean_sales_rep(df)

df = clean_product_name(df)

df = clean_product_category(df)

df = clean_quantity(df)

df = clean_unit_price(df)

df = clean_discount_pct(df)

df = clean_tax_pct(df)

df = clean_sales_amount(df)

df = clean_profit(df)

df = clean_cogs(df)

df = verify_sales(df)

df = clean_currency(df)

df = clean_payment_method(df)

df = clean_status(df)

connection = connection(BASE_DIR)

df.to_sql('medical_report', connection, if_exists='replace', index=False)

print(df.iloc[:, 8: ].tail(30))
# print(df.iloc[df['order_id'] == 'MD-2501-00134'].iloc[:, 8: ])
# print(df.head())
print(len(df)) #original length is 299



