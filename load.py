import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


def bigquery_upload(data):
    """
    Uploads data to Google BigQuery tables.

    Args:
        data (dict): A dictionary containing dataframes to be uploaded.
    """
    # Path to the JSON credentials file for authentication
    key_path = '/path_to_your_file.json'

    # Project ID and dataset ID in BigQuery
    project_id = "my-data-project-392011"
    dataset_id = "bike_analysis"

    # Load credentials from the JSON credentials file
    credentials = service_account.Credentials.from_service_account_file(
        key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    # Create a BigQuery client instance
    client = bigquery.Client(credentials=credentials, project=project_id)

    # Iterate through data and upload to corresponding tables
    for key, value in data.items():
        table_id = f"{project_id}.{dataset_id}.{key}"

        # Configure the load job
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE"
        )

        # Load the dataframe into the specified table
        job = client.load_table_from_dataframe(
            pd.DataFrame(value), table_id, job_config=job_config
        )
        job.result()

        # Get information about the uploaded table
        uploaded_table = client.get_table(table_id)
        print(f"Table '{uploaded_table.table_id}' has been successfully uploaded.")
