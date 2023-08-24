import pandas as pd
import io
import requests
from export import bigquery_upload
from cleaning import cleaning_and_transform

# Path to the CSV file
# Export from Google storage
url = 'https://storage.googleapis.com/bike_analysis_vondal/bikes_data.csv'
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), sep=',')

# Transformation and Cleaning process
data = cleaning_and_transform(df)

# _____________ Upload TO THE BigQuery on GOOGLE CLOUD for next processing __________________
bigquery_upload(data)
