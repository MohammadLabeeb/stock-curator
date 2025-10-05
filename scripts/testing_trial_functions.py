import json
from datetime import datetime

# Load the JSON data from the file
with open('data/filtered_data.json', 'r') as f:
    data = f.read()
    data = json.loads(data)
    print(f"Loaded {len(data)} records from data/filtered_data.json")