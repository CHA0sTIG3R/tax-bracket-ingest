from datetime import datetime
import pandas as pd

def process_irs_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Process the IRS DataFrame to normalize and structure it.
    
    Args:
        df (pd.DataFrame): The DataFrame containing IRS tax data.
    
    Returns:
        pd.DataFrame: A normalized DataFrame with structured tax rates and brackets.
    """
    
    status_rates = {
        "Married Filing Jointly (Rates/Brackets)": (9, 16),
        "Married Filing Separately (Rates/Brackets)": (17, 24),
        "Single Filer (Rates/Brackets)": (1, 8),
        "Head of Household (Rates/Brackets)": (25, 32)
    }
    
    year = datetime.now().year
    greater_than = '>'
    rows = []
    
    for status, (start, end) in status_rates.items():
        
        sub_row = df.iloc[start:end, 1:4].copy()
        
        sub_row.insert(0, 'Year', year)
        sub_row.insert(2, 'For Income >', greater_than)
        
        sub_row.rename(
            columns={
                sub_row.columns[1]: status, 
                sub_row.columns[3]: 'Range Start'
            },
            inplace=True
        )
        
        rows.append(sub_row.reset_index(drop=True))

    # Merge all into one dataframe
    merged_df = pd.concat(rows, axis=1)

    # Drop duplicate 'Year' columns, keep only the first
    merged_df = drop_one_duplicate(merged_df, 'Year')

    return merged_df

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

def dataframe_to_csv(df: pd.DataFrame, filename: str) -> None:
    """Save the DataFrame to a CSV file.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the file to save the DataFrame to.
    """
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
   