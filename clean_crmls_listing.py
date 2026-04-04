

# %%
import pandas as pd

def clean_listing_data(df):
    cols_to_keep = [
        "OriginalListPrice",
        "ListAgentFirstName",
        "ListPrice",
        "ListAgentLastName",
        "LotSizeSquareFeet",
        "BedroomsTotal",
        "PropertyType",
        "PropertySubType",
        "DaysOnMarket"
    ]
    
    df = df[cols_to_keep].copy()
    
    num_cols = [
        "OriginalListPrice",
        "ListPrice",
        "LotSizeSquareFeet",
        "BedroomsTotal",
        "DaysOnMarket"
    ]
    
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.dropna(subset=["OriginalListPrice", "ListPrice"])
    
    df["ListAgentFirstName"] = df["ListAgentFirstName"].fillna("Unknown")
    df["ListAgentLastName"] = df["ListAgentLastName"].fillna("Unknown")
    df["PropertySubType"] = df["PropertySubType"].fillna("Unknown")
    
    return df

# %%
listing = pd.read_csv("CRMLSListing202602.csv")
listing_clean = clean_listing_data(listing)

listing_clean.info()
listing_clean.isna().sum()

# %%
