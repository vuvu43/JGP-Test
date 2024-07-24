import requests
import json
import pandas as pd
from datetime import datetime

headers = {'Content-type': 'application/json'}

# Series IDs for the required CPI data
series_ids = {
    'CUSR0000SA0': 'CPI_All_Items',      # CPI All items, seasonally adjusted
    'CUSR0000SA0L1E': 'CPI_Less_Food_Energy',   # CPI All items, less food and energy, seasonally adjusted
    'CUSR0000SETB': 'CPI_Gasoline'      # CPI Gasoline (all types), seasonally adjusted
}

# Function to fetch data for a single series
def fetch_series_data(series_id):
    data = json.dumps({
        "seriesid": [series_id],
        "startyear": "1959",
        "endyear": "2024"
    })
    response = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
    json_data = response.json()
    return json_data

# Initialize a dictionary to store the combined data
combined_data = {
    "Date": []
}

# Process each series separately
for series_id, series_name in series_ids.items():
    json_data = fetch_series_data(series_id)
    temp_data = {
        "Date": [],
        series_name: []
    }

    # Process the JSON data
    for series in json_data['Results']['series']:
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = float(item['value'])

            if 'M01' <= period <= 'M12':
                date_str = f"{year}-{int(period[1:]):02d}-01"
                temp_data["Date"].append(datetime.strptime(date_str, "%Y-%m-%d"))
                temp_data[series_name].append(value)

    # Create a DataFrame from the temporary data
    df_temp = pd.DataFrame(temp_data)

    # If this is the first series, initialize the combined DataFrame
    if "CPI_All_Items" not in combined_data:
        combined_data["Date"] = temp_data["Date"]
        combined_data[series_name] = temp_data[series_name]
    else:
        # Add the new series data to the combined DataFrame
        combined_data = pd.merge(
            pd.DataFrame(combined_data),
            df_temp,
            on="Date",
            how="outer"
        ).to_dict(orient='list')

# Convert the combined dictionary to a DataFrame
df_combined = pd.DataFrame(combined_data)

# Sort the DataFrame by Date
df_combined.sort_values(by=["Date"], inplace=True)

# Show head of DataFrame
print(df_combined.head())

# Save the DataFrame to a CSV file (optional)
df_combined.to_csv('cpi_combined_data.csv', index=False, date_format='%Y-%m-%d')

print("Question 1 done")
