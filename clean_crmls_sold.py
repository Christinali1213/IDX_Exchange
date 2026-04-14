
# %%
import pandas as pd

def cap_outliers(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df[col] = df[col].clip(lower=lower, upper=upper)
    return df

def clean_sold_data(df):
    cols_to_keep = [
        "OriginalListPrice",
        "ListAgentFirstName",
        "ListPrice",
        "ListAgentLastName",
        "LotSizeSquareFeet",
        "BedroomsTotal",
        "PropertyType",
        "PropertySubType",
        "DaysOnMarket",
        "ClosePrice",
        "CloseDate",
        "BuyerAgentFirstName",
        "BuyerAgentLastName",
        "BuyerOfficeName"
    ]
    
    df = df[cols_to_keep].copy()

    df = df.drop_duplicates()
    
    num_cols = [
        "OriginalListPrice",
        "ListPrice",
        "LotSizeSquareFeet",
        "BedroomsTotal",
        "DaysOnMarket",
        "ClosePrice"
    ]
    
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["CloseDate"] = pd.to_datetime(df["CloseDate"], errors="coerce")
    
    df = df.dropna(subset=["OriginalListPrice", "ListPrice", "ClosePrice"])

    for col in ["LotSizeSquareFeet", "BedroomsTotal", "DaysOnMarket"]:
        df[col] = df[col].fillna(df[col].median())

    for col in ["OriginalListPrice", "ListPrice", "ClosePrice", "LotSizeSquareFeet"]:
        df = cap_outliers(df, col)
    
    df["ListAgentFirstName"] = df["ListAgentFirstName"].fillna("Unknown")
    df["ListAgentLastName"] = df["ListAgentLastName"].fillna("Unknown")
    df["PropertyType"] = df["PropertyType"].fillna("Unknown")
    df["PropertySubType"] = df["PropertySubType"].fillna("Unknown")
    df["BuyerAgentFirstName"] = df["BuyerAgentFirstName"].fillna("Unknown")
    df["BuyerAgentLastName"] = df["BuyerAgentLastName"].fillna("Unknown")
    df["BuyerOfficeName"] = df["BuyerOfficeName"].fillna("Unknown")

    str_cols = [
        "ListAgentFirstName", "ListAgentLastName",
        "BuyerAgentFirstName", "BuyerAgentLastName",
        "BuyerOfficeName", "PropertyType", "PropertySubType"
    ]
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip().str.title()

    df["SaleToListRatio"] = df["ClosePrice"] / df["ListPrice"]
    df["PricePerSqFt"] = df["ClosePrice"] / df["LotSizeSquareFeet"]
    df["PriceDrop"] = df["OriginalListPrice"] - df["ListPrice"]
    df["PriceDropPct"] = (df["PriceDrop"] / df["OriginalListPrice"]) * 100
    
    return df

# %%
sold = pd.read_csv("CRMLSSold202602.csv")
sold_clean = clean_sold_data(sold)

sold_clean.info()
print("\nMissing values:\n", sold_clean.isna().sum())
print(f"\nRows: {len(sold_clean):,} | Date range: {sold_clean['CloseDate'].min().date()} → {sold_clean['CloseDate'].max().date()}")
