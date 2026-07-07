import logging

import pandas as pd
import pytz
from factory import get_printer, get_storage
from storage_port import StoragePort

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Default columns to select from raw events
DEFAULT_EVENT_COLUMNS = [
    "time",
    "start_time",
    "end_time",
    "shift_start",
    "shift_end",
    "production_date",
    "production_target",
    "produced",
    "machine_id",
    "machine_name",
    "scrapped",
    "event_duration",
    "status_code",
    "part_number",
    "ideal_cycle_time",
]

PART_CONFIGURATION_COLUMNS = ["id", "machine_id", "seconds_per_part", "multiplier", "name"]


def lambda_handler(event, context):
    """
    Lambda function to read JSONL data from S3, transform it, and optionally save to S3

    Expected event structure:
    {
        "s3_input_path": "s3://<PATH>/data.jsonl",
        "local_timezone": "Europe/London",
        "save_to_s3": false,
        "events_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/raw_events_20260701.jsonl",
        "part_configuration_path": "s3://bax-bxty-thf-data-warehouse.s3.eu-central-1.amazonaws.com/warehouse/thf/curated/dim_part_configurations/part_configuration.parquet"
    }
    """
    storage = get_storage()
    printer = get_printer()

    # Get parameters from event
    local_timezone = event.get("local_timezone", "Europe/London")
    events_path = event.get("events_path")
    part_configuration_path = event.get("part_configuration_path")

    # Validate s3_input_path
    if not events_path:
        return {
            "statusCode": 400,
            "body": {"message": "s3_input_path is required in event"},
        }

    # Read JSONL data from S3
    try:
        events_df = storage.read_json(path=events_path)
        # Select only required columns
        events_df = events_df[DEFAULT_EVENT_COLUMNS]
        # styled_dataframe(events_df, title="📊 Machine Events")
        # display_dataframe(events_df, title="Events", max_rows=10)
        printer.display_dataframe(df=events_df, title="Events", max_rows=10)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": f"Error reading JSONL from S3: {str(e)}"},
        }

        # Read part configuration data from S3
    try:
        part_configuration_df = storage.read_parquet(path=part_configuration_path)
        part_configuration_df = part_configuration_df[PART_CONFIGURATION_COLUMNS]
        # printer.display_dataframe(df=part_configuration_df, title="Part Configuration", max_rows=10)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {"message": f"Error reading part configuration from S3: {str(e)}"},
        }

    # Remove records with null machine_id from events_df
    events_df = events_df[events_df["machine_id"].notna()].copy()

    # Ensure compatible data types for merge keys before merging
    # Handle NaN values in machine_id columns by filling with 0, then convert to int64
    events_df["machine_id"] = events_df["machine_id"].fillna(0).astype("int64")
    part_configuration_df["machine_id"] = part_configuration_df["machine_id"].fillna(0).astype("int64")

    # printer.display_dataframe(events_df, title="Cleaned events", max_rows=10)
    merged_df = events_df.merge(
        part_configuration_df, left_on=["machine_id", "part_number"], right_on=["machine_id", "name"], how="left"
    )
    result_df = transform(df=merged_df, local_timezone=local_timezone)
    printer.display_dataframe(result_df, title="Events with Part Configuration", max_rows=10)

    # Optional: Save to S3 using awswrangler
    if event.get("save_to_s3", False):
        s3_output_path = event.get("s3_output_path")

        load(df=result_df, storage=storage, s3_path=s3_output_path)

        return {
            "statusCode": 200,
            "body": {
                "message": "Data successfully saved to S3",
                "records_count": len(result_df),
                "s3_path": s3_output_path,
            },
        }
    return {
        "statusCode": 200,
        "body": {"message": "Data successfully processed", "records_count": len(merged_df)},
    }


def transform(df: pd.DataFrame, local_timezone: str) -> pd.DataFrame:
    """
    Transform and normalize a raw pandas DataFrame extracted from OpenSearch.

    This function performs the following transformations:
    - Converts date/time fields to timezone-aware UTC timestamps
    - Casts numeric columns to integer type, coercing invalid values to 0
    - Converts the `time` field to Europe/London timezone
    - Creates a `time_local` field for localized timestamp handling
    - Drops rows where `time_local` could not be parsed
    - Adds partition columns (`year`, `month`, `day`) derived from `time_local`

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing raw OpenSearch records. The DataFrame is expected
        to include at least the following columns when available:
        - time
        - start_time
        - end_time
        - shift_start
        - shift_end
        - production_date
        - produced
        - machine_id
        - scrapped
        - event_duration
        - status_code

    Returns
    -------
    pandas.DataFrame
        A transformed DataFrame with normalized datetime columns, integer-typed
        numeric fields, a localized `time_local` column, and partition columns
        (`year`, `month`, `day`) added for downstream storage or analysis.

    Notes
    -----
    - Invalid datetime values are coerced to `NaT`.
    - Invalid numeric values are converted to `0`.
    - The function currently uses the `Europe/London` timezone for localization.
    - Rows with invalid `time_local` values are removed before returning the result.
    """
    # Remove those in which the machine_id is equals to zero
    df = df[df["machine_id"] != 0].copy()

    # Ensure fields to be datetime values.
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True, errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], utc=True, errors="coerce")
    df["shift_start"] = pd.to_datetime(df["shift_start"], utc=True, errors="coerce")
    df["shift_end"] = pd.to_datetime(df["shift_end"], utc=True, errors="coerce")
    df["production_date"] = pd.to_datetime(df["production_date"], utc=True, errors="coerce")

    # ENSURE IN IN SOME COLUMNS
    int_cols = [
        # EVENTS
        "produced",
        "machine_id",
        "scrapped",
        "event_duration",
        "status_code",
        "production_target",
        # PART CONFIGURATION
        "multiplier",
    ]

    for col in int_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    # MODIFY TIMEZONE
    df["time"] = pd.to_datetime(df["time"], utc=True)
    target_tz = pytz.timezone(local_timezone)  # or your timezone
    df["time_local"] = df["time"].dt.tz_convert(target_tz)

    # PARTITION
    df["time_local"] = pd.to_datetime(df["time_local"], errors="coerce")  # CONTINUE SAIDS CAN BRING ERRORS
    df = df.dropna(subset=["time_local"])

    # Create partition columns
    df["year"] = df["time_local"].dt.year.astype(str)
    df["month"] = df["time_local"].dt.month.map(lambda x: f"{x:02d}")
    df["day"] = df["time_local"].dt.day.map(lambda x: f"{x:02d}")
    return df


def load(df: pd.DataFrame, storage: StoragePort, s3_path: str):
    """
    Load a transformed pandas DataFrame into an Amazon S3 data lake in Parquet format.

    This function writes the provided DataFrame to an S3 path as a partitioned Parquet dataset
    using awswrangler. The output is organized by the following partition columns:

    - machine_id
    - year
    - month
    - day

    The destination S3 path is taken from the `event` payload if provided; otherwise, it falls
    back to a default warehouse path based on the `plant_prefix`.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to be written to S3. It is expected to already contain the columns
        required for partitioning (`machine_id`, `year`, `month`, `day`).

    s3_path : str
        S3 path where the DataFrame will be written.

    Returns
    -------
    None
        This function does not return a value. It writes the dataset directly to S3.

    Side Effects
    ------------
    - Writes data to S3 in Parquet format.
    - Uses `mode='overwrite_partitions'`, which overwrites only partitions present in the
      incoming DataFrame.

    Notes
    -----
    - The function assumes the DataFrame contains valid values for the partition columns.
    - If any partition column is missing, `wr.s3.to_parquet()` will raise an error.
    - The S3 path should point to a location intended for partitioned dataset storage.
    """
    storage.write_parquet(df=df, path=s3_path)
