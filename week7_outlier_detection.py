"""
Week 7 – Outlier Detection and Data Quality
IDX Exchange MLS Analytics Program

Applies IQR-based outlier detection to ClosePrice, LivingArea, and DaysOnMarket
for both the Sold and Listing datasets. Adds flag columns rather than deleting
records outright, saves a full flagged dataset and a clean filtered dataset,
and prints a before/after comparison of dataset size and median values.
"""

import pandas as pd
import numpy as np

sold     = pd.read_csv("sold_cleaned_w45.csv",    low_memory=False)
listings = pd.read_csv("listing_cleaned_w45.csv", low_memory=False)
IQR_FIELDS = ["ClosePrice", "LivingArea", "DaysOnMarket"]


def compute_iqr_bounds(series: pd.Series, multiplier: float = 1.5) -> tuple:
    Q1  = series.quantile(0.25)
    Q3  = series.quantile(0.75)
    IQR = Q3 - Q1
    return Q1 - multiplier * IQR, Q3 + multiplier * IQR


def add_outlier_flags(df: pd.DataFrame, fields: list) -> pd.DataFrame:
    """
    For each field, add a boolean flag column '<field>_outlier_flag'.
    A record is flagged if it falls outside the IQR bounds OR is <= 0
    (business rule: non-positive values are always invalid for these fields).
    Also adds a composite 'any_outlier_flag' column.
    """
    df = df.copy()
    flag_cols = []

    for field in fields:
        if field not in df.columns:
            print(f"  [WARNING] '{field}' not found – skipping.")
            continue

        col      = pd.to_numeric(df[field], errors="coerce")
        lower, upper = compute_iqr_bounds(col.dropna())

        flag = (col <= 0) | (col < lower) | (col > upper)
        flag_col = f"{field}_outlier_flag"
        df[flag_col] = flag
        flag_cols.append(flag_col)

        n_flagged = flag.sum()
        pct       = 100 * n_flagged / len(df)
        print(f"  {field:25s}  lower={lower:>12,.1f}  upper={upper:>14,.1f}  "
              f"flagged={n_flagged:>6,} ({pct:.1f}%)")
    if flag_cols:
        df["any_outlier_flag"] = df[flag_cols].any(axis=1)

    return df


def before_after_summary(df_raw: pd.DataFrame,
                          df_clean: pd.DataFrame,
                          fields: list,
                          label: str) -> None:
    """Print a before/after comparison of row count and median values."""
    print(f"\n{'─'*60}")
    print(f"  {label}  –  Before / After Comparison")
    print(f"{'─'*60}")
    print(f"  {'Metric':<30} {'Before':>12} {'After':>12}  {'Δ':>8}")
    print(f"  {'─'*28} {'─'*12} {'─'*12}  {'─'*8}")

    # Row count
    n_before = len(df_raw)
    n_after  = len(df_clean)
    print(f"  {'Row count':<30} {n_before:>12,} {n_after:>12,}  "
          f"{n_after - n_before:>+8,}")

    # Median per field
    for field in fields:
        if field not in df_raw.columns:
            continue
        col_b = pd.to_numeric(df_raw[field],   errors="coerce")
        col_a = pd.to_numeric(df_clean[field], errors="coerce")
        med_b = col_b.median()
        med_a = col_a.median()
        delta = med_a - med_b
        print(f"  {'Median ' + field:<30} {med_b:>12,.1f} {med_a:>12,.1f}  "
              f"{delta:>+8,.1f}")
    print()


# Process SOLD dataset 
print("=" * 60)
print("SOLD DATASET")
print("=" * 60)
sold_flagged = add_outlier_flags(sold, IQR_FIELDS)
sold_clean = sold_flagged[~sold_flagged["any_outlier_flag"]].copy()
flag_cols_to_drop = [c for c in sold_clean.columns if c.endswith("_outlier_flag")]
sold_clean_export = sold_clean.drop(columns=flag_cols_to_drop)

before_after_summary(sold, sold_clean, IQR_FIELDS, "SOLD")

#  Process LISTING dataset 
print("=" * 60)
print("LISTING DATASET")
print("=" * 60)
listing_flagged = add_outlier_flags(listings, IQR_FIELDS)
listing_clean = listing_flagged[~listing_flagged["any_outlier_flag"]].copy()
flag_cols_to_drop = [c for c in listing_clean.columns if c.endswith("_outlier_flag")]
listing_clean_export = listing_clean.drop(columns=flag_cols_to_drop)

before_after_summary(listings, listing_clean, IQR_FIELDS, "LISTING")

# save results to CSV files
sold_flagged.to_csv("sold_flagged_w7.csv",       index=False)
listing_flagged.to_csv("listing_flagged_w7.csv", index=False)
sold_clean_export.to_csv("sold_clean_w7.csv",       index=False)
listing_clean_export.to_csv("listing_clean_w7.csv", index=False)

print("Saved: sold_flagged_w7.csv")
print("Saved: listing_flagged_w7.csv")
print("Saved: sold_clean_w7.csv")
print("Saved: listing_clean_w7.csv")
print("\nDone ✓")
