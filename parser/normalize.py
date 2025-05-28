from datetime import datetime
import pandas as pd

def normalize_scraped_data(scraped_data: pd.DataFrame) -> pd.DataFrame:
    """Normalize the scraped data into the desired format. 
    <p>
    The format: 
    <pre>
    "Year","Married Filing Jointly (Rates/Brackets)","","","Married Filing Separately (Rates/Brackets)","","","Single Filer (Rates/Brackets)","","","Head of Household (Rates/Brackets)","","","Notes:"
    </pre>
    <p>
    Example:
    <code>
        "2021","10.0%",">","$0","10.0%",">","$0","10.0%",">","$0","10.0%",">","$0","Last law to change rates was the Tax Cuts and Jobs Act of 2017."
    </code>

    Args:
        scraped_data (pd.DataFrame): The raw scraped data containing tax brackets and rates.

    Returns:
        pd.DataFrame: A DataFrame with normalized columns and rows, ready for further processing or analysis.
    """  
    normalized_rows = []
    
    year = datetime.now().year
    single = scraped_data.iloc[1:8, 1:4].to_dict(orient='records')
    married_jointly = scraped_data.iloc[9:16, 1:4].to_dict(orient='records')
    married_separately = scraped_data.iloc[17:24, 1:4].to_dict(orient='records')
    head_of_household = scraped_data.iloc[25:32, 1:4].to_dict(orient='records')
    notes = ""
    
    for i in range(len(single)):
        
        row = {
            "Year": year,
            "Married Filing Jointly (Rates/Brackets)": f"{married_jointly[i]['Rate']}",
            "": ">",
            " ": f"{married_jointly[i]['Range']}",
            "Married Filing Separately (Rates/Brackets)": f"{married_separately[i]['Rate']}",
            "  ": ">",  
            "   ": f"{married_separately[i]['Range']}", 
            "Single Filer (Rates/Brackets)": f"{single[i]['Rate']}",
            "    ": ">",  
            "     ": f"{single[i]['Range']}", 
            "Head of Household (Rates/Brackets)": f"{head_of_household[i]['Rate']}",
            "      ": ">",  
            "       ": f"{head_of_household[i]['Range']}", 
            "Notes:": notes
        }
        
        normalized_rows.append(row)
    
    normalized_data = pd.DataFrame(normalized_rows)
    return normalized_data


def dataframe_to_csv(df: pd.DataFrame, filename: str) -> None:
    """Save the DataFrame to a CSV file.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the file to save the DataFrame to.
    """
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
   