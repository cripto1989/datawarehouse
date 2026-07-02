import json
import logging
import os
from typing import Any, Dict, List

import awswrangler as wr
import pandas as pd
from db import execute_query, get_db_connection

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Environment variables for database connection
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = int(os.environ.get("DB_PORT", 3306))


def save_results_to_s3(results: List[Dict[str, Any]], s3_path: str) -> str:
    """
    Saves query results to S3 in Parquet format using AWS Wrangler.

    Args:
        results: List of dictionaries containing query results
        s3_path: S3 path where to save the parquet file (e.g., s3://bucket-name/path/file.parquet)

    Returns:
        str: S3 path where the file was saved

    Raises:
        Exception: If saving to S3 fails
    """
    try:
        # Ensure s3_path ends with .parquet extension
        if not s3_path.endswith(".parquet"):
            s3_path = f"{s3_path}.parquet"
            print(f"Added .parquet extension to s3_path: {s3_path}")

        # Convert results to pandas DataFrame
        df = pd.DataFrame(results)
        print(f"DataFrame created with shape: {df.shape}")
        print(f"DataFrame columns: {df.columns.tolist()}")
        print(f"DataFrame dtypes:\n{df.dtypes}")

        # Save to S3 using AWS Wrangler (handles compression and partitioning)
        print(f"Saving parquet file to S3: {s3_path}")
        wr.s3.to_parquet(
            df=df,
            path=s3_path,
            index=False,
            compression="snappy",
        )

        print(f"Successfully saved parquet file to S3: {s3_path}")
        return s3_path

    except Exception as e:
        error_message = f"Failed to save results to S3: {str(e)}"
        print(error_message)
        raise Exception(error_message)


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event object containing:
            - query: SQL query string (optional, defaults to SELECT * FROM machine_partconfiguration;)
            - params: Optional tuple of parameters for parameterized queries
            - s3_path: S3 path where to save the parquet file (e.g., s3://bucket-name/path/file.parquet)
        context: Lambda context object

    Returns:
        dict: Response with status code and body containing query results and S3 save status
    """
    connection = None
    try:
        query = event.get(
            "query", "SELECT * FROM machine_partconfiguration pc INNER JOIN machine_part p ON pc.part_id = p.id;;"
        )
        params = event.get("params", None)
        s3_path = event.get("s3_path")

        print(f"Lambda invoked with event: {json.dumps(event)}")

        # Establish database connection
        connection = get_db_connection(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME, port=DB_PORT)

        # Execute the query
        results = execute_query(connection, query, params)

        # Save results to S3 in parquet format if s3_path is provided
        s3_save_path = None
        if s3_path:
            s3_save_path = save_results_to_s3(results, s3_path)

        # Return successful response
        response_body = {
            "message": "Query executed successfully",
            "rowCount": len(results),
        }

        if s3_save_path:
            response_body["s3_path"] = s3_save_path
            response_body["message"] = "Query executed successfully and results saved to S3"

        return {
            "statusCode": 200,
            "body": response_body,
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Error executing query", "error": str(e)})}

    finally:
        # Always close the database connection
        if connection:
            connection.close()
            print("Database connection closed")
