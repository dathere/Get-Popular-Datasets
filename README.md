# Get-Popular-Datasets

This repository contains a script that downloads popular datasets from the CKAN portal.

## Requirements

- Python 3.6 or higher
- requests

## Installation

```bash
pip install requests
```

## Usage

```bash
python get_popular_datasets.py
```

## Configuration

You can configure the script by changing the values in the `config.ini` file.

```ini
[default]
url = https://catalog.data.gov   # The URL of the CKAN portal.
rows = 100                       # The number of datasets to search for.
output_file = output.csv         # The name of the output file.
organization = org_name          # The name of the organization to search for.
```

## Report

The script generates a CSV file with the following columns:

- organization
- title
- url
- metadata_created
- metadata_modified
- total number of views