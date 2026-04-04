# %%
import pandas as pd

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
        "CloseDate" 
    ]
    
    df = df[cols_to_keep].copy()
    
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
    
    df = df.dropna(subset=["OriginalListPrice", "ListPrice", "ClosePrice"])
    
    df["ListAgentFirstName"] = df["ListAgentFirstName"].fillna("Unknown")
    df["ListAgentLastName"] = df["ListAgentLastName"].fillna("Unknown")
    df["PropertySubType"] = df["PropertySubType"].fillna("Unknown")
    
    return df

# %%
sold = pd.read_csv("CRMLSSold202602.csv")
sold_clean = clean_sold_data(sold)

sold_clean.info()
sold_clean.isna().sum()


