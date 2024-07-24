import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px

headers = {'Content-type': 'application/json'}

# Series IDs for the required CPI data
series_id = [
    'CUSR0000SA0L1E'   # CPI All items, less food and energy, seasonally adjusted
]

# Create the request payload
data = json.dumps({
    "seriesid": series_id,
    "startyear": "2019",
    "endyear": "2024"
})

# Make the API request
response = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
json_data = response.json()

# Function to process series data and save to CSV
def process_and_save_series(series_data, series_name):
    data_dict = {
        "Date": [],
        series_name: []
    }
    
    for item in series_data['data']:
        year = item['year']
        period = item['period']
        value = item['value']

        if 'M01' <= period <= 'M12':
            # Create date string in the format MM/YYYY
            date_str = f"{year}-{int(period[1:]):01d}-1"
            data_dict["Date"].append(datetime.strptime(date_str, "%Y-%m-%d"))
            data_dict[series_name].append(value)
    
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data_dict)
    
    # Sort the DataFrame by Date
    df.sort_values(by=["Date"], inplace=True)
    
    # Save the DataFrame to a CSV file
    df.to_csv(f'{series_name}.csv', index=False, date_format='%Y-%m-%d')


# Process and save series
#process_and_save_series(series_id[0], "CPI_Less_Food_Energy")

# Load the data
df = pd.read_csv('CPI_Less_Food_Energy.csv')

# Convert the 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

# Calculate the year-over-year percentage variation
df['YoY_Percentage_Variation'] = df['CPI_Less_Food_Energy'].pct_change(periods=12) * 100

# Create the chart using Plotly
fig = px.line(df, x='Date', y='YoY_Percentage_Variation',
              title='Year-over-Year Percentage Variation of CPI',
              labels={'YoY_Percentage_Variation': 'YoY % Variation'})

# Update layout for better visualization
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Year-over-Year Percentage Variation',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True),
    template='plotly_white'
)

# Show the chart
fig.write_html('cpi_yoy_variation.html')
    
print("Question 2 done")
