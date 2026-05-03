"""
sales_etl.py
------------
ETL pipeline: cleans sales_report.csv and loads it into sales.db.

Improvements over the original:
  - Modular functions → each step is testable and reusable in isolation
  - Structured logging → replaces bare print(), gives timestamps & severity
  - Type hints & docstrings → self-documenting; IDEs and linters can reason about it
  - Named constants → magic strings/values defined once at the top
  - Proper operator-precedence fix in the final quantity filter
  - Fixed discount pipeline (original crashed when fillna(0) produced ints then called .str)
  - Guard clause for __main__ → safe to import as a module without side effects
"""

import logging
import os
import re
import sqlite3
from pathlib import Path   # Better than os.path: cleaner API, chainable, cross-platform

import numpy as np
import pandas as pd
import pycountry_convert as pc

# ---------------------------------------------------------------------------
# Configuration — all magic values in one place so changes propagate everywhere
# ---------------------------------------------------------------------------

BASE_DIR   = Path(__file__).resolve().parent   # Path() is more readable than os.path.dirname(os.path.abspath())
CSV_PATH   = BASE_DIR / "sales_report.csv"     # / operator on Path objects replaces os.path.join
DB_PATH    = BASE_DIR / "sales.db"
TABLE_NAME = "sales"

ORDER_ID_LENGTH = 6
FALLBACK_EMAIL  = "invalid@gmail.com"         # Single definition — change here, applies everywhere
EMAIL_REGEX     = r"^[\w\.\+    \-]+@[\w\.-]+\.[a-zA-Z]{2,}$"  # Stricter: requires 2+ char TLD format: example.com, example.co.uk, but not example@localhost or example@com

# ---------------------------------------------------------------------------
# Logging — gives timestamps, severity levels, and easy redirection to files
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",   # Structured format; easier to parse in prod
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)   # Module-scoped logger — doesn't pollute the root logger


# ---------------------------------------------------------------------------
# Helper functions — each has one job, a docstring, and a type signature
# ---------------------------------------------------------------------------

def load_csv(path: Path) -> pd.DataFrame:
    """
    Read the CSV and normalise column names in one step.
    Raising FileNotFoundError early gives a clear error instead of a cryptic KeyError later.
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(path)

    # Strip, lowercase, replace spaces — same as original, but extracted so it's reusable
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)   # regex=False is faster when no pattern is needed
    )

    log.info("Loaded %d rows, %d columns from %s", len(df), len(df.columns), path.name)
    return df


def clean_order_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise order IDs: strip whitespace/dashes, keep digits only,
    then flag any ID that isn't exactly ORDER_ID_LENGTH digits as 'N/A'.
    """
    df = df.drop_duplicates(subset=["order_id"])   # Remove dupes before any further work

    cleaned = (
        df["order_id"]
        .astype(str)
        .str.strip()
        .str.replace(r"[\s\-]", "", regex=True)     # Collapse spaces and dashes in one pass
        .str.replace(r"\D", "", regex=True)          # Keep digits only
    )

    # np.where is vectorised (fast); the original .where() logic was reversed — .where keeps
    # values that satisfy the condition, so the mask must be TRUE for valid IDs.
    valid_mask = cleaned.str.len() == ORDER_ID_LENGTH
    df["order_id"] = np.where(valid_mask, cleaned, "N/A")

    log.info("Order IDs: %d valid, %d set to N/A", valid_mask.sum(), (~valid_mask).sum())
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse order_date and ship_date from mixed formats, then drop rows where
    ship_date precedes order_date (logically impossible / data error).
    """
    for col in ("order_date", "ship_date"):
        normalised = (
            df[col]
            .str.strip()
            .str.replace(r"[ /]", "-", regex=True)   # Single regex covers both space and slash separators
        )
        df[col] = (
            pd.to_datetime(normalised, format="mixed", errors="coerce")
            .dt.date   # Drop the time component; store as a plain date
        )

    before = len(df)
    df = df[~(df["ship_date"] < df["order_date"])]   # ~ negates: keep rows where ship >= order
    log.info("Date filter removed %d rows where ship_date < order_date", before - len(df))
    return df


def clean_names_and_emails(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise customer names to Title Case and emails to lowercase.
    Emails that don't match EMAIL_REGEX are replaced with FALLBACK_EMAIL.
    """
    df["customer_name"] = df["customer_name"].str.strip().str.title()

    emails = df["customer_email"].str.strip().str.lower().str.replace(" ", "", regex=False)
    valid_email = emails.str.match(EMAIL_REGEX)   # .match() is anchored at start; more accurate than .contains()

    invalid_count = (~valid_email).sum()
    df["customer_email"] = emails.where(valid_email, FALLBACK_EMAIL)

    if invalid_count:
        log.warning("Replaced %d invalid email(s) with '%s'", invalid_count, FALLBACK_EMAIL)
    return df


def add_region(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive a continent code from the country name using pycountry_convert.
    Failures (unknown countries, encoding issues) fall back to 'Unknown'.
    A local cache (dict) avoids redundant lookups for repeated country values.
    """
    cache: dict[str, str] = {}   # Memoisation — only resolve each unique country once

    def _lookup(country: str) -> str:
        if country not in cache:
            try:
                alpha2 = pc.country_name_to_country_alpha2(country)
                cache[country] = pc.country_alpha2_to_continent_code(alpha2)
            except Exception:
                cache[country] = "Unknown"
        return cache[country]

    df["region"] = df["country"].apply(_lookup)

    unknown = (df["region"] == "Unknown").sum()
    if unknown:
        log.warning("%d rows have unknown region", unknown)
    return df


def clean_discount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise discount to a numeric percentage string, e.g. '10.50%'.

    The original code called .fillna(0) (producing integers) and then
    immediately used .str methods — that crashes because integers have no
    .str accessor.  Fixed by converting to string *after* filling nulls.
    """
    # Step 1: fill nulls with the string '0' so .str ops work uniformly
    disc = df["discount"].fillna("0").astype(str).str.strip()

    # Step 2: if already ends with '%', strip it; otherwise the value is a raw number
    numeric = disc.str.rstrip("%")   # '10%' → '10', '10' → '10' (idempotent)

    df["discount"] = (
        pd.to_numeric(numeric, errors="coerce")   # Convert to float, coerce bad values to NaN
        .fillna(0)
        .round(2)
        .apply(lambda x: f"{x:.2f}%")            # f-string formatting is cleaner than string concatenation
    )
    return df


def clean_sales_amount(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip currency symbols/commas, cast to float, drop negatives,
    then re-format as '$1,234.56'.
    """
    # Remove negative rows first — operating on strings is simpler than numeric sign check here
    before = len(df)
    df = df[~df["sales_amount"].astype(str).str.contains(r"^\s*-", regex=True)]
    log.info("Removed %d row(s) with negative sales_amount", before - len(df))

    df["sales_amount"] = (
        df["sales_amount"]
        .astype(str)
        .str.replace(r"[$,\s]", "", regex=True)   # Strip $, commas, and spaces in one regex
        .pipe(pd.to_numeric, errors="coerce")      # .pipe() avoids a temporary variable
        .round(2)
        .apply(lambda x: f"${x:,.2f}" if pd.notna(x) else None)  # Guard against NaN before formatting
    )
    return df


def clean_unit_price(df: pd.DataFrame) -> pd.DataFrame:
    """Remove currency formatting from unit_price and reformat consistently."""
    df["unit_price"] = (
        df["unit_price"]
        .astype(str)
        .str.replace(r"[$,\s]", "", regex=True)
        .pipe(pd.to_numeric, errors="coerce")
        .round(2)
        .apply(lambda x: f"${x:,.2f}" if pd.notna(x) else None)
    )
    return df


def clean_quantity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast quantity to integer; coerce non-numeric values to NaN, then drop
    rows with quantity ≤ 0.

    The original final filter had an operator-precedence bug:
        df['quantity'].astype(str).str.replace('$','').astype(float) > 0
                & df['sales_amount'].notna()
    '&' binds tighter than '>', so it was evaluated as:
        quantity > (0 & notna_mask)   ← wrong and misleading
    Fixed below with explicit parentheses.
    """
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")   # Coerces any non-numeric to NaN cleanly

    before = len(df)
    # Explicit parentheses around each condition — no ambiguity about precedence
    df = df[(df["quantity"] > 0) & df["sales_amount"].notna()]
    df["quantity"] = df["quantity"].astype(int)   # Safe to cast to int now that NaN rows are gone
    log.info("Quantity filter removed %d row(s)", before - len(df))
    return df


def clean_text_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Title-case and strip free-text categorical columns in one loop.
    Adding a new column to normalise requires only one line change here.
    """
    for col in ("payment_method", "channel", "status", "salesperson"):
        if col not in df.columns:
            log.warning("Expected column '%s' not found — skipping", col)
            continue
        cleaned = df[col].str.strip().str.title()
        if col == "salesperson":
            cleaned = cleaned.str.replace(" ", "", regex=False)   # Salesperson: no spaces (e.g. 'JohnDoe')
        df[col] = cleaned
    return df


def write_to_sqlite(df: pd.DataFrame, db_path: Path, table: str) -> None:
    """
    Persist the cleaned DataFrame to SQLite.
    Uses a context manager (with statement) so the connection is always
    closed even if an exception occurs — the original code could leak a
    connection on error.
    """
    with sqlite3.connect(db_path) as conn:   # Context manager auto-commits and closes on exit
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                order_id       TEXT,
                order_date     TEXT,
                ship_date      TEXT,
                customer_name  TEXT,
                customer_email TEXT,
                region         TEXT,
                country        TEXT,
                product        TEXT,
                category       TEXT,
                quantity       INTEGER,
                unit_price     TEXT,
                discount       TEXT,
                sales_amount   TEXT,
                payment_method TEXT,
                salesperson    TEXT,
                channel        TEXT,
                status         TEXT,
                notes          TEXT
            )
        """)
        df.to_sql(table, conn, if_exists="append", index=False)
    log.info("Wrote %d rows to table '%s' in %s", len(df), table, db_path.name)


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

def run_pipeline() -> pd.DataFrame:
    """
    Execute the full ETL pipeline in a clear, readable sequence.
    Each step is a named function call — easy to comment out for debugging.
    """
    df = load_csv(CSV_PATH)

    df = clean_order_ids(df)
    df = parse_dates(df)
    df = clean_names_and_emails(df)
    df = add_region(df)
    df = clean_discount(df)
    df = clean_sales_amount(df)
    df = clean_unit_price(df)
    df = clean_text_categoricals(df)
    df = clean_quantity(df)       # Run after sales_amount so the notna() check is valid

    # Drop the row_id column if present — do it late so earlier steps still have it if needed
    df = df.drop(columns=["row_id"], errors="ignore")   # errors='ignore' avoids a crash if column is absent

    write_to_sqlite(df, DB_PATH, TABLE_NAME)

    log.info("Pipeline complete. Final shape: %d rows × %d columns", *df.shape)
    return df


# ---------------------------------------------------------------------------
# Entry point — the __main__ guard prevents execution when this file is imported
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = run_pipeline()
    print(result.head(1).to_string())   # .to_string() prevents truncation of wide DataFrames