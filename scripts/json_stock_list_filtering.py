# 'data.json' contains complete list of BOD contracts available for trading on Upstox in JSON format.
# source: https://upstox.com/developer/api-documentation/instruments/

# this script loads data.json file and removes all items not having "instrument_type": "EQ", 
# then saves it to filtered_data.json

import json
from datetime import datetime

# Load the JSON data from the file
with open('data/data.json', 'r') as f:
    data = f.read()
    data = json.loads(data)
    print(f"Loaded {len(data)} records from data/raw/stock_data.json")

    # Filter the data
    filtered_data = [item for item in data if item.get("instrument_type") == "EQ"]

    # Save the filtered data to a new JSON file
    with open('data/processed/filtered_stock_data.json', 'w') as f:
        json.dump(filtered_data, f, indent=4)

    print(f"Saved {len(filtered_data)} records to data/processed/filtered_stock_data.json")