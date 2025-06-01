import pytest
from tax_bracket_ingest.parser.parser import parse_html, parse_table, parse_irs_data, parse_irs_data_to_dataframe
import pandas as pd

def test_parse_html():
    """
    Test the parse_html function to ensure it correctly parses HTML content.
    """
    html_content = """
    <html>
        <body>
            <h2>Test Header</h2>
            <table>
                <tr><th>Income Range</th><td>$0 - $10,000</td></tr>
                <tr><th>Tax Rate</th><td>10%</td></tr>
            </table>
        </body>
    </html>
    """
    result = parse_html(html_content)
    assert isinstance(result, dict), "Result should be a dictionary."
    assert "Test Header" in result, "Header 'Test Header' should be present."
    assert "Income Range" in result["Test Header"]['table'], "Table should contain 'Income Range'."
    assert "Tax Rate" in result["Test Header"]['table'], "Table should contain 'Tax Rate'."
    

def test_parse_table():
    """
    Test the parse_table function to ensure it correctly parses a table element.
    """
    table_html = """
    <table>
        <tr><th>Income Range</th><td>$0 - $10,000</td></tr>
        <tr><th>Tax Rate</th><td>10%</td></tr>
    </table>
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')
    
    result = parse_table(table)
    assert isinstance(result, dict), "Result should be a dictionary."
    assert "Income Range" in result, "Table should contain 'Income Range'."
    assert "Tax Rate" in result, "Table should contain 'Tax Rate'."
    assert result["Income Range"] == "$0 - $10,000", "Income Range should match."
    assert result["Tax Rate"] == "10%", "Tax Rate should match."
    
def test_parse_irs_data():
    """
    Test the parse_irs_data function to ensure it correctly parses IRS data.
    """
    html_content = """
    <html>
        <body>
            <h2>Married Filing Jointly</h2>
            <table>
                <tr><th>Income Range</th><td>$0 - $10,000</td></tr>
                <tr><th>Tax Rate</th><td>10%</td></tr>
            </table>
            <h2>Single</h2>
            <table>
                <tr><th>Income Range</th><td>$0 - $5,000</td></tr>
                <tr><th>Tax Rate</th><td>12%</td></tr>
            </table>
        </body>
    </html>
    """
    result = parse_irs_data(html_content)
    assert isinstance(result, dict), "Result should be a dictionary."
    assert "Married Filing Jointly" in result, "Should contain 'Married Filing Jointly'."
    assert "Single" in result, "Should contain 'Single'."
    assert "Income Range" in result["Married Filing Jointly"]['table'], "Table should contain 'Income Range'."
    assert "Tax Rate" in result["Single"]['table'], "Table should contain 'Tax Rate'."
    
def test_parse_irs_data_to_dataframe():
    """
    Test the parse_irs_data_to_dataframe function to ensure it converts IRS data to a DataFrame.
    """
    irs_data = {
        "Married Filing Jointly": {
            "table": {
                "Income Range": "$0 - $10,000",
                "Tax Rate": "10%"
            }
        },
        "Single": {
            "table": {
                "Income Range": "$0 - $5,000",
                "Tax Rate": "12%"
            }
        }
    }
    
    df = parse_irs_data_to_dataframe(irs_data)
    assert isinstance(df, pd.DataFrame), "Result should be a DataFrame."
    assert not df.empty, "DataFrame should not be empty."
    assert 'Header' in df.columns, "DataFrame should contain 'Header' column."
    assert 'Rate' in df.columns, "DataFrame should contain 'Rate' column."
    assert 'Range' in df.columns, "DataFrame should contain 'Range' column."
    assert len(df) == 4, "DataFrame should have 4 rows for the two headers and their corresponding rates and ranges."

if __name__ == "__main__":
    pytest.main([__file__])  
