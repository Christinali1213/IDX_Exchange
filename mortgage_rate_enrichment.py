import pandas as pd

# load the MLS datasets
sold = pd.read_csv('CRMLSSold_Combined.csv')
listings = pd.read_csv('CRMLSListing_Combined.csv')

# pulling straight from FRED — no API key needed
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url)
mortgage.columns = ['date', 'rate_30yr_fixed']
mortgage['date'] = pd.to_datetime(mortgage['date'])

# FRED is weekly but our MLS data is monthly, so we average down
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

# derive a year-month key from each dataset so we have something to join on
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')
listings['year_month'] = pd.to_datetime(
    listings['ListingContractDate']).dt.to_period('M')

sold_with_rates     = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# anything other than 0 here means something didn't join right
print(sold_with_rates['rate_30yr_fixed'].isnull().sum())
print(listings_with_rates['rate_30yr_fixed'].isnull().sum())

print(sold_with_rates[['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']].head())

# save enriched datasets
sold_with_rates.to_csv('CRMLSSold_Combined_with_rates.csv', index=False)
listings_with_rates.to_csv('CRMLSListing_Combined_with_rates.csv', index=False)
