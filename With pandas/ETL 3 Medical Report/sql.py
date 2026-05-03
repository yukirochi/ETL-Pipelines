import sqlite3
import pandas as pd
from pathlib import Path


def connection(BASE_DIR: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(BASE_DIR / "medical_report.db")
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS medical_report (
        order_id TEXT,
        invoice_id TEXT,
        order_date TEXT,
        ship_date TEXT,
        customer_id TEXT,
        customer_name TEXT,
        customer_email TEXT,
        region TEXT,
        channel TEXT,
        customer_type TEXT,
        sales_rep TEXT,
        product_name TEXT,
        product_category TEXT,
        quantity INTEGER,
        unit_price TEXT,
        discount_pct TEXT,
        tax_pct TEXT,
        sales_amount TEXT,
        cogs TEXT,
        profit TEXT,
        currency TEXT,
        payment_method TEXT,
        status TEXT
    )''')
    connection.commit()
    return connection