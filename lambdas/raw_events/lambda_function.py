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

    if start_time and end_time:
        logger.info("Start time and end time received.")
        start_time = validate_datetime_string(start_time, "start_time")
        end_time = validate_datetime_string(end_time, "end_time")
        validate_time_range(start_time, end_time)
    else:
        today = datetime.now(ZoneInfo(local_timezone)).date() + timedelta(days=-1)
        today = today.strftime("%Y-%m-%d")
        start_time, end_time = get_date_range(today)
    logger.info(f"From {start_time} to {end_time}.")

    filename = f"raw_events_{end_time.replace('-', '')[:8]}.jsonl"
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
    partition_path = build_partition_path(end_time)
    return load(
        data=data,
        s3_path=s3_path,
        filename=filename,
        partition_path=partition_path,
    )


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
            "factory_order",
            # THIS CAN BE DELETED IF NOT REQUIRED
            "start_time",
            "end_time",
            "shift_id",
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
    return data


def load(data: List[Dict], s3_path: str, filename: str, partition_path: str = ""):
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

    # Ensure s3_path and partition_path end with /
    if not s3_path.endswith("/"):
        s3_path = s3_path + "/"

    if partition_path and not partition_path.endswith("/"):
        partition_path = partition_path + "/"

    # Construct full S3 path
    full_s3_path = f"{s3_path}{partition_path}{filename}"

    # Convert JSON lines to string
    json_lines = "\n".join(json.dumps(record, default=str) for record in data)

    # Parse S3 path to extract bucket and key
    s3_uri_parts = full_s3_path.replace("s3://", "").split("/", 1)
    bucket = s3_uri_parts[0]
    key = s3_uri_parts[1] if len(s3_uri_parts) > 1 else filename

    # Write to S3
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=bucket, Key=key, Body=json_lines.encode("utf-8"), ContentType="application/x-ndjson")

    logger.info(f"Successfully loaded {len(data)} records to {full_s3_path}")
    return {
        "statusCode": 200,
        "body": {
            "message": "Successfully loaded raw events to S3.",
            "records_loaded": len(data),
            "s3_path": full_s3_path,
        },
    }


def build_partition_path(end_time: str) -> str:
    """Build a partition-style S3 prefix from an end_time string."""

    end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
    return end_dt.strftime("%Y/%m/%d")


def get_date_range(date: str) -> tuple[str, str]:
    """
    Convert a date string (YYYY-MM-DD) into a start/end datetime range.

    The start datetime is the previous day at 23:00:00.
    The end datetime is the provided day at 22:59:59.

    Returns:
        Tuple of (start_datetime, end_datetime) formatted as:
        %Y-%m-%dT%H:%M:%S
    """

    date_obj = datetime.strptime(date, "%Y-%m-%d")

    start_datetime = (date_obj - timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
    end_datetime = date_obj.replace(hour=22, minute=59, second=59, microsecond=0)

    start_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return start_str, end_str


def validate_datetime_string(value: str, field_name: str = "datetime") -> str:
    """
    Validate a datetime string in the exact format YYYY-MM-DDTHH:MM:SS.

    Parameters
    ----------
    value : str
        The datetime string to validate.
    field_name : str
        The name of the field being validated, used in error messages.

    Returns
    -------
    str
        The validated datetime string.

    Raises
    ------
    ValueError
        If the value is not a string or does not match the expected format.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string in the format YYYY-MM-DDTHH:MM:SS.")

    try:
        parsed_value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid datetime string in the format YYYY-MM-DDTHH:MM:SS.") from exc

    if parsed_value.strftime("%Y-%m-%dT%H:%M:%S") != value:
        raise ValueError(f"{field_name} must match the exact format YYYY-MM-DDTHH:MM:SS.")

    return value


def validate_time_range(start_time: str, end_time: str) -> None:
    """
    Validate that end_time is greater than start_time.

    Parameters
    ----------
    start_time : str
        Start datetime string in the format YYYY-MM-DDTHH:MM:SS.
    end_time : str
        End datetime string in the format YYYY-MM-DDTHH:MM:SS.

    Raises
    ------
    ValueError
        If end_time is not greater than start_time.
    """
    start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
    end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

    if end_dt <= start_dt:
        raise ValueError("end_time must be greater than start_time.")
