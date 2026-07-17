import json
import logging
import os
from typing import Any, Dict, List

import awswrangler as wr
import pandas as pd
from db import execute_query, get_db_connection
from schemas import SCHEMAS

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Environment variables for database connection
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = int(os.environ.get("DB_PORT", 3306))


def save_results_to_s3(results: List[Dict[str, Any]], s3_path: str, schema: str) -> str:
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
            dtype=SCHEMAS.get(schema, None),  # Use schema if provided, else None
        )

        print(f"Successfully saved parquet file to S3: {s3_path}")
        return s3_path

    except Exception as e:
        error_message = f"Failed to save results to S3: {str(e)}"
        print(error_message)
        raise Exception(error_message)


def lambda_handler(event, context):
    """
    AWS Lambda handler function that processes multiple queries.

    Args:
        event: Lambda event object containing:
            - queries: List of query objects, each containing:
                - query: SQL query string
                - path: S3 path where to save the parquet file
        context: Lambda context object

    Returns:
        dict: Response with status code and body containing processing results for all queries
    """
    connection = None
    try:
        print(f"Lambda invoked with event: {json.dumps(event)}")

        # Extract queries from event
        queries = event.get("queries", [])

        if not queries:
            return {"statusCode": 400, "body": json.dumps({"message": "No queries provided in event"})}

        # Establish database connection
        connection = get_db_connection(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME, port=DB_PORT)

        # Process results for tracking successes and failures
        processed_queries = []
        failed_queries = []
        total_rows = 0

        # Iterate through each query
        for index, query_obj in enumerate(queries):
            try:
                query = query_obj.get("query")
                s3_path = query_obj.get("path")
                schema = query_obj.get("schema")

                if not query:
                    failed_queries.append({"index": index, "error": "Query not provided in query object"})
                    continue

                if not s3_path:
                    failed_queries.append({"index": index, "error": "S3 path not provided in query object"})
                    continue

                print(f"Processing query {index + 1}/{len(queries)}: {query[:100]}...")

                # Execute the query
                results = execute_query(connection, query, None)
                row_count = len(results)
                total_rows += row_count

                # Save results to S3
                try:
                    s3_save_path = save_results_to_s3(results, s3_path, schema=schema)
                    processed_queries.append(
                        {
                            "index": index,
                            "query": query[:100] + "..." if len(query) > 100 else query,
                            "s3_path": s3_save_path,
                            "rowCount": row_count,
                            "status": "success",
                        }
                    )
                except Exception as s3_error:
                    failed_queries.append(
                        {
                            "index": index,
                            "query": query[:100] + "..." if len(query) > 100 else query,
                            "error": f"Failed to save to S3: {str(s3_error)}",
                        }
                    )

            except Exception as query_error:
                failed_queries.append({"index": index, "error": str(query_error)})

        # Prepare response
        response_body = {
            "message": f"Processed {len(queries)} queries",
            "totalRows": total_rows,
            "successCount": len(processed_queries),
            "failureCount": len(failed_queries),
            "processedQueries": processed_queries,
        }

        if failed_queries:
            response_body["failedQueries"] = failed_queries
            status_code = 207 if processed_queries else 500  # 207 Partial Success or 500 if all failed
        else:
            status_code = 200

        return {
            "statusCode": status_code,
            "body": response_body,
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Error processing queries", "error": str(e)})}

    finally:
        # Always close the database connection
        if connection:
            connection.close()
            print("Database connection closed")
