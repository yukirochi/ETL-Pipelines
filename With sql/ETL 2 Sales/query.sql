DROP TABLE IF EXISTS sales;

CREATE TABLE sales AS
SELECT DISTINCT * FROM read_csv_auto('sales_report.csv') WHERE order_id IS NOT NULL;


-- UPDATE sales
-- SET customer_name = CASE
--     WHEN customer_name IS NULL THEN 'Unknown'
--     ELSE TRIM(LOWER(customer_name))
-- END;

CREATE OR REPLACE FUNCTION CLEAN_NAME(name) AS
    COALESCE(TRIM(LOWER(LEFT())), 'unknown'); --if the first part is null return the second part

UPDATE sales
SET customer_name = CLEAN_NAME(customer_name)
;

UPDATE sales
SET sales_amount = CASE
    -- Check if the first character is '$'
    WHEN LEFT(TRIM(CAST(sales_amount AS VARCHAR)), 1) = '$' 
    -- Remove '$', then cast to integer (or decimal)
    THEN CAST(REPLACE(CAST(sales_amount AS VARCHAR), '$', '') AS INTEGER)
    ELSE CAST(sales_amount AS INTEGER)
END;

SELECT * FROM sales;

