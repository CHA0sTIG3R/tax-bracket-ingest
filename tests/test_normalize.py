import pytest
from tax_bracket_ingest.parser.normalize import (
    process_irs_dataframe, 
    drop_one_duplicate, 
    dataframe_to_csv
)
import pandas as pd
from datetime import datetime

@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame to test the normalization process."""
    data = {
        'Header': [
            
            '2024 tax rates for a single taxpayer', '2024 tax rates for a single taxpayer',
            '2024 tax rates for a single taxpayer', '2024 tax rates for a single taxpayer',
            '2024 tax rates for a single taxpayer', '2024 tax rates for a single taxpayer',
            '2024 tax rates for a single taxpayer', '2024 tax rates for a single taxpayer',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing jointly or qualifying surviving spouse',
            'Married filing separately', 'Married filing separately',
            'Married filing separately', 'Married filing separately',
            'Married filing separately', 'Married filing separately',
            'Married filing separately', 'Married filing separately',
            'Head of household', 'Head of household', 'Head of household',
            'Head of household', 'Head of household', 'Head of household',
            'Head of household', 'Head of household'
        ],
            'Rate': [
            'Tax rate', '10%', '12%', '22%', '24%', '32%', '35%', '37%',
            'Tax rate', '10%', '12%', '22%', '24%', '32%', '35%', '37%',
            'Tax rate', '10%', '12%', '22%', '24%', '32%', '35%', '37%',
            'Tax rate', '10%', '12%', '22%', '24%', '32%', '35%', '37%'
        ],
        'Range': [
            'on taxable income from . . .', '$0', '$11,601', '$47,151', '$100,526',
            '$191,951', '$243,726', '$609,351', 'on taxable income from . . .',
            '$0', '$23,201', '$94,301', '$201,051', '$383,901', '$487,451',
            '$731,201', 'on taxable income from . . .', '$0', '$11,601',
            '$47,151', '$100,526', '$191,951', '$243,726', '$365,601',
            'on taxable income from . . .', '$0', '$16,551', '$63,101',
            '$100,501', '$191,951', '$243,701', '$609,351'
        ]
    }
    
    return pd.DataFrame(data)

def test_process_irs_dataframe(sample_dataframe):
    """Test the process_irs_dataframe function to ensure it normalizes the DataFrame correctly."""
    normalized_df = process_irs_dataframe(sample_dataframe)
    
    # Check if the DataFrame has the expected columns
    expected_columns = ['Year', 'Married Filing Jointly (Rates/Brackets)', 
                        'Married Filing Separately (Rates/Brackets)', 
                        'Single Filer (Rates/Brackets)', 
                        'Head of Household (Rates/Brackets)', 
                        'For Income >', 'Range Start']
    assert all(col in normalized_df.columns for col in expected_columns), "Normalized DataFrame should contain expected columns."
    
    current_year = datetime.now().year
    assert (normalized_df['Year'] == current_year).all(), "Year column should contain the current year."
    expected_row_count = 7 
    assert len(normalized_df) == expected_row_count, f"Normalized DataFrame should have {expected_row_count} rows."
    
def test_drop_one_duplicate(sample_dataframe):
    """Test the drop_one_duplicate function to ensure it removes column name duplicates correctly."""
    df_copy_1 = sample_dataframe.copy()
    df_copy_2 = sample_dataframe.copy()
    df_copy_3 = sample_dataframe.copy()
    df_with_duplicates = pd.concat([df_copy_1, df_copy_2, df_copy_3], axis=1)
    
    assert df_with_duplicates.columns.tolist().count('Header') > 1, "There should be multiple 'Header' columns before dropping duplicates."
    len_before = len(df_with_duplicates.columns)
    
    cleaned_df = drop_one_duplicate(df_with_duplicates, 'Header')
    
    len_after = len(cleaned_df.columns)  
    assert len_after == len_before - 2, "One duplicate 'Header' column should be removed."
    assert cleaned_df.columns.tolist().count('Header') == 1, "There should be only one 'Header' column in the cleaned DataFrame."
    
def test_dataframe_to_csv(sample_dataframe, tmp_path):
    """Test the dataframe_to_csv function to ensure it saves the DataFrame to a CSV file correctly."""
    # Define a temporary file path
    temp_file = tmp_path / "test_output.csv"
    
    # Call the function to save the DataFrame to CSV
    dataframe_to_csv(sample_dataframe, temp_file)
    
    # Check if the file was created
    assert temp_file.exists(), "CSV file should be created."
    
    # Read the CSV file back into a DataFrame
    loaded_df = pd.read_csv(temp_file)
    
    # Check if the loaded DataFrame matches the original sample DataFrame
    pd.testing.assert_frame_equal(loaded_df, sample_dataframe, check_dtype=True, check_like=True)
    

if __name__ == "__main__":
    pytest.main()