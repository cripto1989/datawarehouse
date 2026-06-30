import json
from typing import Any, Dict, List

import pymysql


def get_db_connection(host: str, user: str, password: str, db_name: str, port: int = 3306):
    """
    Establishes and returns a connection to the Aurora MySQL database.

    Returns:
        pymysql.connections.Connection: Database connection object

    Raises:
        Exception: If connection fails
    """
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            port=port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        print(f"Successfully connected to database: {db_name}")
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
