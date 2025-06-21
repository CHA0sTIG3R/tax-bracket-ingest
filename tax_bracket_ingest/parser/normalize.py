# tax_bracket_ingest/parser/normalize.py
import pandas as pd
import numpy as np

def process_irs_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Process the IRS DataFrame to normalize and structure it.
    
    Args:
        df (pd.DataFrame): The DataFrame containing IRS tax data.
    
    Returns:
        pd.DataFrame: A normalized DataFrame with structured tax rates and brackets.
    """
    
    status_rates = {
        "Married Filing Jointly (Rates/Brackets)": (9, 16, 'MFJ Range Start'),
        "Married Filing Separately (Rates/Brackets)": (17, 24, 'MFS Range Start'),
        "Single Filer (Rates/Brackets)": (1, 8, 'S Range Start'),
        "Head of Household (Rates/Brackets)": (25, 32, 'HOH Range Start')
    }
    
    year = int(df['Header'][0].split(' ')[0])
    rows = []
    
    for status, (start, end, name) in status_rates.items():
        
        sub_row = df.iloc[start:end, 1:4].copy()
        
        sub_row.insert(0, 'Year', year)
        
        sub_row.rename(
            columns={
                sub_row.columns[1]: status, 
                sub_row.columns[2]: name
            },
            inplace=True
        )
        
        rows.append(sub_row.reset_index(drop=True))

    # Merge all into one dataframe
    merged_df = pd.concat(rows, axis=1)

    # Drop duplicate 'Year' columns, keep only the first
    merged_df = drop_one_duplicate(merged_df, 'Year')
    
    # add range end columns
    merged_df = populate_range_end(merged_df)

    return merged_df

def populate_range_end(df: pd.DataFrame) -> pd.DataFrame:
    
    range_start_cols = [col for col in df.columns if col.endswith("Range Start")]

    for col in range_start_cols:
        
        numeric_start = (
            df[col]
            .astype(str)
            .str.replace(r'[^\d.]', '', regex=True)
            .replace(r'^\s*$', np.nan, regex=True)
            .astype(float)
        )
        
        numeric_end = numeric_start.shift(-1) - 1
        
        formatted_end = numeric_end.apply(
            lambda x: f"${int(x):,}" if pd.notnull(x) else np.nan
        )

        ins_idx = df.columns.get_loc(col) + 1
        df.insert(ins_idx, col.replace("Start", "End"), formatted_end)

    return df

def drop_one_duplicate(df: pd.DataFrame, duplicate_col: str) -> pd.DataFrame:
    """Drop all but one occurrence of a specified duplicate column in a DataFrame.
    Args:
        df (pd.DataFrame): The DataFrame to process.
        duplicate_col (str): The name of the column to check for duplicates.
    Returns:
        pd.DataFrame: The DataFrame with duplicates removed, keeping only the first occurrence.
    """
    cols = df.columns.tolist()
    seen = {}
    new_cols = []
    for col in cols:
        if col == duplicate_col:
            count = seen.get(col, 0)
            if count == 0:
                new_cols.append(True)
            else:
                new_cols.append(False)
            seen[col] = count + 1
        else:
            new_cols.append(True)
    df = df.loc[:, new_cols]
    return df
    
   