from setuptools import setup, find_packages

setup(
    name='tax_bracket_ingest',
    version='0.1.0',
    author='Hamza Olowu',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'beautifulsoup4>=4.9.0',
        'requests>=2.24.0',
        'pytest>=6.0.0'
    ],
    description='A package to scrape, parse, and normalize IRS tax bracket data.'
)