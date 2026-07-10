import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List
from zoneinfo import ZoneInfo

import boto3
from opensearchpy import OpenSearch
from search_client import OpenSearchClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function to query OpenSearch and return filtered data as DataFrame

    Expected event structure:
    {
        "start_time": "2024-01-01T00:00:00",
        "end_time": "2024-01-31T23:59:59",
        "index_name": "your-index-name",
        "local_timezone": "Europe/London"
    }
    """

    # Get parameters from event
    start_time = event.get("start_time")
    end_time = event.get("end_time")
    index_name = event.get("index_name", "your-default-index")
    local_timezone = event.get("local_timezone", "Europe/London")

    # OpenSearch configuration from environment variables
    opensearch_endpoint = os.environ.get("OPENSEARCH_ENDPOINT", "")
    region = os.environ.get("REGION", "us-east-2")
    username = os.environ.get("OPENSEARCH_USERNAME")
    password = os.environ.get("OPENSEARCH_PASSWORD")

    if not start_time or end_time:
        yesterday = datetime.now(ZoneInfo(local_timezone)) + timedelta(days=-1)
        yesterday = yesterday.date().strftime("%Y-%m-%d")
        start_time, end_time = get_date_range(yesterday)

    opensearch_client = OpenSearchClient(
        region=region,
        endpoint=opensearch_endpoint,
        username=username,
        password=password,
    ).build_client()

    data = extract(
        client=opensearch_client,
        start_time=start_time,
        end_time=end_time,
        index_name=index_name,
    )
    s3_path = event.get("s3_path")
    load(data=data, s3_path=s3_path)


def extract(client: OpenSearch, start_time: str, end_time: str, index_name: str) -> List[Dict]:
    """
    Query OpenSearch for documents whose `time` field falls within a given range.

    This function performs a range query on the `time` field of the specified
    OpenSearch index and retrieves all matching documents using scroll pagination.
    It returns the `_source` portion of each hit as a dictionary.

    Parameters
    ----------
    client : OpenSearch
        An initialized OpenSearch client used to execute the search and scroll requests.
    start_time : str
        Start of the time range filter, in a format accepted by OpenSearch.
    end_time : str
        End of the time range filter, in a format accepted by OpenSearch.
    index_name : str
        The name of the OpenSearch index to search.

    Returns
    -------
    List[Dict]
        A list of dictionaries representing the matching documents. Each dictionary
        contains the `_source` fields from OpenSearch. If `status_code` is missing,
        it is set to `-1`.

    Notes
    -----
    - Uses scroll pagination with a 2-minute scroll context to fetch all results.
    - Limits the initial query size to 10,000 records.
    - Clears the scroll context after retrieval.
    """

    query = {
        "_source": [
            "time",
            "produced",
            "event_duration",
            "machine_id",
            "machine_name",
            "production_target",
            "scrapped",
            "status_code",
            "part_number",
            "ideal_cycle_time",
            "multiplier",
            # THIS CAN BE DELETED IF NOT REQUIRED
            "start_time",
            "end_time",
            "shift_start",
            "shift_end",
            "production_date",
        ],
        "query": {"bool": {"must": [{"range": {"time": {"gte": start_time, "lte": end_time}}}]}},
        "size": 10000,  # Adjust based on your needs
    }

    response = client.search(
        index=index_name,
        body=query,
        scroll="2m",  # Keep the search context alive for 2 minutes
    )

    # # Extract hits
    hits = response["hits"]["hits"]
    scroll_id = response["_scroll_id"]

    # Scroll through all results if there are more than 10000
    while len(response["hits"]["hits"]) > 0:
        logger.info("Hitting the scroll")
        response = client.scroll(scroll_id=scroll_id, scroll="2m")
        hits.extend(response["hits"]["hits"])
        if len(response["hits"]["hits"]) == 0:
            break

    # Clear the scroll context
    client.clear_scroll(scroll_id=scroll_id)

    # Extract source data from hits, handling missing status_code
    data = []
    for hit in hits:
        source = hit.get("_source", {})
        source["status_code"] = source.get("status_code", -1)
        data.append(source)
    logger.info(f"FINAL DATA {data}")
    return data


def load(data: List[Dict], s3_path: str):
    """
    Load raw event data to Amazon S3 as a JSON file.

    This function writes the provided list of dictionaries to an S3 path as a JSON Lines file
    (newline-delimited JSON), where each line is a separate JSON object. This is an optimized
    format for large datasets and is compatible with many data processing tools.

    The file is saved with a timestamp to ensure uniqueness and avoid overwriting existing data.

    Parameters
    ----------
    data : List[Dict]
        A list of dictionaries representing raw event records from OpenSearch. Each dictionary
        contains the source fields from OpenSearch documents.

    s3_path : str
        S3 path (directory) where the JSON file will be written. Should be in the format
        's3://bucket-name/path/to/directory/'. The function will append a timestamped filename.

    Returns
    -------
    None
        This function does not return a value. It writes the dataset directly to S3.

    Side Effects
    ------------
    - Writes data to S3 in JSON Lines format (.jsonl).
    - Creates a new file with a timestamp in the filename to ensure uniqueness.

    Notes
    -----
    - Uses JSON Lines format (one JSON object per line) for efficient processing.
    - Each record is serialized with default=str to handle non-serializable types (datetime, etc.).
    - The S3 path should include a trailing slash and should point to a valid S3 location.

    Raises
    ------
    ValueError
        If the data list is empty.
    Exception
        If S3 write operation fails due to permission or connectivity issues.
    """
    if not data:
        raise ValueError("No data to load. The data list is empty.")

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"raw_events_{timestamp}.jsonl"

    # Ensure s3_path ends with /
    if not s3_path.endswith("/"):
        s3_path = s3_path + "/"

    # Construct full S3 path
    full_s3_path = f"{s3_path}{filename}"

    # Convert JSON lines to string
    json_lines = "\n".join(json.dumps(record, default=str) for record in data)

    # Parse S3 path to extract bucket and key
    s3_uri_parts = full_s3_path.replace("s3://", "").split("/", 1)
    bucket = s3_uri_parts[0]
    key = s3_uri_parts[1] if len(s3_uri_parts) > 1 else filename

    # Write to S3
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=bucket, Key=key, Body=json_lines.encode("utf-8"), ContentType="application/x-ndjson")

    print(f"Successfully loaded {len(data)} records to {full_s3_path}")


def get_date_range(date: str) -> tuple[str, str]:
    """
    Convert a date string (YYYY-MM-DD) into a start/end datetime range.

    Returns:
        Tuple of (start_datetime, end_datetime) formatted as:
        %Y-%m-%dT%H:%M:%S
    """
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    start_datetime = date_obj.replace(hour=23, minute=0, second=0, microsecond=0)
    end_datetime = date_obj.replace(hour=22, minute=59, second=59, microsecond=0)

    start_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return start_str, end_str
