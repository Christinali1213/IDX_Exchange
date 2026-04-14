import os
import pandas as pd
from datetime import datetime

import crmls_listed
import crmls_sold

DATA_DIR    = 'data'
START_YEAR  = 2024
START_MONTH = 1

def get_last_completed_month():
    today = datetime.today()
    if today.month == 1:
        return datetime(today.year - 1, 12, 1)
    return datetime(today.year, today.month - 1, 1)


def month_range(start_year, start_month):
    last = get_last_completed_month()
    current = datetime(start_year, start_month, 1)
    while current <= last:
        yield current.year, current.month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print('Authenticating...')
    token = crmls_sold.get_token()  # one token, works for both
    print('Token obtained.\n')

    sold_frames   = []
    listed_frames = []

    for year, month in month_range(START_YEAR, START_MONTH):
        label = f'{year}{month:02d}'

        # ── SOLD ──────────────────────────────
        sold_path = os.path.join(DATA_DIR, f'CRMLSSold{label}.csv')
        if os.path.exists(sold_path):
            print(f'  [SOLD]   {label} — loading from disk')
            df_sold = pd.read_csv(sold_path, low_memory=False)
        else:
            print(f'  [SOLD]   {label} — fetching from API...')
            df_sold = crmls_sold.fetch_month(token, year, month, sold_path)

        if df_sold is not None and len(df_sold) > 0:
            df_sold['source_file'] = f'CRMLSSold{label}.csv'
            sold_frames.append(df_sold)

        # ── LISTED ────────────────────────────
        listed_path = os.path.join(DATA_DIR, f'CRMLSListing{label}.csv')
        if os.path.exists(listed_path):
            print(f'  [LISTED] {label} — loading from disk')
            df_listed = pd.read_csv(listed_path, low_memory=False)
        else:
            print(f'  [LISTED] {label} — fetching from API...')
            df_listed = crmls_listed.fetch_month(token, year, month, listed_path)

        if df_listed is not None and len(df_listed) > 0:
            df_listed['source_file'] = f'CRMLSListing{label}.csv'
            listed_frames.append(df_listed)

    # ── COMBINE & SAVE ────────────────────────
    print()
    if sold_frames:
        sold_combined = pd.concat(sold_frames, ignore_index=True)
        sold_combined.to_csv('CRMLSSold_Combined.csv', index=False)
        print(f'CRMLSSold_Combined.csv    — {len(sold_combined):,} total rows')

    if listed_frames:
        listed_combined = pd.concat(listed_frames, ignore_index=True)
        listed_combined.to_csv('CRMLSListing_Combined.csv', index=False)
        print(f'CRMLSListing_Combined.csv — {len(listed_combined):,} total rows')

    print('\nDone.')


if __name__ == '__main__':
    main()