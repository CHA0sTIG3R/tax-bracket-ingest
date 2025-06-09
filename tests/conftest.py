import pytest
import pandas as pd

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

@pytest.fixture
def sample_html():
    return """
    <html>
        <body>
            <h2>2024 tax rates for a single taxpayer</h2>
            <table>
                <thead>
		            <tr>
			            <th>Tax rate</th>
			            <th>on taxable income from . . .</th>
			            <th>up to . . .</th>
		            </tr>
	            </thead>
                <tbody>
		            <tr>
                        <td>10%</td>
                        <td>$0</td>
                        <td>$11,600</td>
                    </tr>
                    <tr>
                        <td>12%</td>
                        <td>$11,601</td>
                        <td>$47,150</td>
                    </tr>
                </tbody>
            </table>
            <h2>Married Filing Jointly</h2>
            <table>
                <thead>
		            <tr>
			            <th>Tax rate</th>
			            <th>on taxable income from . . .</th>
			            <th>up to . . .</th>
		            </tr>
	            </thead>
                <tbody>
		            <tr>
                        <td>10%</td>
                        <td>$0</td>
                        <td>$11,600</td>
                    </tr>
                    <tr>
                        <td>12%</td>
                        <td>$11,601</td>
                        <td>$47,150</td>
                    </tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    
@pytest.fixture
def sample_table_html():
    return """
    <table>
        <thead>
            <tr>
                <th>Tax rate</th>
                <th>on taxable income from . . .</th>
                <th>up to . . .</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>10%</td>
                <td>$0</td>
                <td>$11,600</td>
            </tr>
            <tr>
                <td>12%</td>
                <td>$11,601</td>
                <td>$47,150</td>
            </tr>
        </tbody>
    </table>
    """
