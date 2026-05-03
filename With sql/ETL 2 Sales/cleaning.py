import duckdb

connection = duckdb.connect('sales_report.db')

with open('query.sql','r') as f:
    connection.execute(f.read())



connection.sql('SELECT * FROM sales ').show()
