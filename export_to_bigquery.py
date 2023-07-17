import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# _____________ IMPORT TO THE BigQuery on GOOGLE CLOUD for next processing __________________

# Path to your JSON credentials file
key_path = '/Users/matous/Downloads/my-data-project-392011-42c40c443d36.json'

# Project ID and dataset ID in BigQuery
project_id = "my-data-project-392011"
dataset_id = "bike_analysis"

credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
# Construct a BigQuery client object.
client = bigquery.Client(credentials=credentials,project=project_id)


for key, value in data.items():
    table_id = "{}.{}.{}".format(project_id, dataset_id, key)

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE")

    job = client.load_table_from_dataframe(
        pd.DataFrame(value), table_id, job_config=job_config
    )
    job.result()

    data = client.get_table(table_id)
    print('Table: {} is successfully sent'.format(key))
