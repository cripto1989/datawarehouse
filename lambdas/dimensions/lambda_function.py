import json
import os
from typing import Any, Dict, List

import pymysql

# Environment variables for database connection
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = int(os.environ.get("DB_PORT", 3306))


def get_db_connection():
    """
    Establishes and returns a connection to the Aurora MySQL database.

    Returns:
        pymysql.connections.Connection: Database connection object

    Raises:
        Exception: If connection fails
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        print(f"Successfully connected to database: {DB_NAME}")
        return connection
    except pymysql.Error as e:
        error_message = f"Database connection failed: {str(e)}"
        print(error_message)
        raise Exception(error_message)


def execute_query(connection, query: str, params: tuple = None) -> List[Dict[str, Any]]:
    """
    Executes a SQL query against the Aurora database.

    Args:
        connection: Database connection object
        query: SQL query string
        params: Optional tuple of parameters for parameterized queries

    Returns:
        List[Dict]: List of dictionaries containing query results

    Raises:
        Exception: If query execution fails
    """
    try:
        with connection.cursor() as cursor:
            print(f"Executing query: {query}")
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Fetch all results
            results = cursor.fetchall()
            print(f"Query executed successfully. Rows returned: {len(results)}")
            print(f"Results: {json.dumps(results, indent=2, default=str)}")

            return results
    except pymysql.Error as e:
        error_message = f"Query execution failed: {str(e)}"
        print(error_message)
        raise Exception(error_message)


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event object
        context: Lambda context object

    Returns:
        dict: Response with status code and body containing query results
    """
    connection = None
    try:
        query = event.get("query", "SELECT * FROM machine_partconfiguration;")
        params = event.get("params", None)

        print(f"Lambda invoked with event: {json.dumps(event)}")

        # Establish database connection
        connection = get_db_connection()

        # Execute the query
        results = execute_query(connection, query, params)

        # Return successful response
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Query executed successfully", "results": results, "rowCount": len(results)}, default=str
            ),
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "Error executing query", "error": str(e)})}

    finally:
        # Always close the database connection
        if connection:
            connection.close()
            print("Database connection closed")
