import awswrangler as wr
import numpy as np
import pandas as pd
from schemas import downtime_schema


def lambda_handler(event, context):
    """
    {
        "events_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/raw/events/2026/07/01/raw_events_20260701_machines_84_85_86_87_155.jsonl",
        "machines_status_code_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_machines_status_code/machines_status_code.parquet",
        "shifts_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_shifts/shifts.parquet",
        "machines_groups_hierarchy_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_machines_groups_hierarchy/machines_groups_hierarchy.parquet",
        "s3_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/fact_downtime/"
    }
    """
    events_path = event.get("events_path", "")
    machines_status_code_path = event.get("machines_status_code_path", "")
    shifts_path = event.get("shifts_path", "")
    machines_groups_hierarchy_path = event.get("machines_groups_hierarchy_path", "")
    s3_path = event.get("s3_path", "")

    events_df = pd.read_json(events_path, lines=True)
    machines_status_code_df = pd.read_parquet(machines_status_code_path)
    shifts_df = pd.read_parquet(shifts_path)
    machines_groups_hierarchy_df = pd.read_parquet(machines_groups_hierarchy_path)

    # Sorting by machine_id and time
    events_df = events_df.sort_values(by=["machine_id", "time"], ascending=[True, True])

    # Finding the position of the "status_code" column in the DataFrame
    status_code_position = events_df.columns.get_loc("status_code")

    events_df.insert(status_code_position + 1, "next_status_code", events_df["status_code"].shift(-1).astype("Int64"))

    # Finding the position of the "next_status_code" column in the DataFrame
    next_status_code_position = events_df.columns.get_loc("next_status_code")

    # Creating a boolean mask for rows where the status_code is 999 or 9999 and the next_status_code is 100
    is_transition_to_100 = (events_df["status_code"].isin([999, 9999]) & events_df["next_status_code"].eq(100)).fillna(
        False
    )

    # Inserting the "status_transition_flag" column after the "next_status_code" column
    events_df.insert(next_status_code_position + 1, "no_of_stops", is_transition_to_100.astype("int"))

    machines_status_code_df = machines_status_code_df[
        ["id", "code", "description", "s.id", "name", "planned_down", "unplanned_down"]
    ].rename(
        columns={
            "id": "downtime_reason_minor_id",
            "description": "downtime_reason_minor",
            "s.id": "downtime_reason_major_id",
            "name": "downtime_reason_major",
            "planned_down": "is_planned_downtime",
            "unplanned_down": "is_unplanned_downtime",
        }
    )

    events_df = events_df.merge(machines_status_code_df, how="left", left_on="status_code", right_on="code")
    downtime_type_position = events_df.columns.get_loc("is_unplanned_downtime")
    downtime_type = np.select(
        [
            events_df["is_unplanned_downtime"].eq(1).fillna(False).to_numpy(dtype=bool),
            events_df["is_planned_downtime"].eq(1).fillna(False).to_numpy(dtype=bool),
        ],
        [
            "Unplanned",
            "Planned",
        ],
        default=None,
    )
    events_df.insert(
        downtime_type_position + 1,
        "downtime_type",
        downtime_type,
    )

    shifts_df = shifts_df[["id", "name", "color"]].rename(
        columns={"id": "shift_id", "name": "shift_name", "color": "shift_color"}
    )

    events_df = events_df.merge(shifts_df, how="left", left_on="shift_id", right_on="shift_id")

    events_df = events_df.merge(machines_groups_hierarchy_df, how="left", left_on="machine_id", right_on="machine_id")

    # Converting the "time", "shift_start", and "shift_end" columns to datetime format
    events_df["time"] = pd.to_datetime(events_df["time"], errors="coerce")
    events_df["production_date"] = pd.to_datetime(events_df["production_date"], errors="coerce")
    events_df["shift_start"] = pd.to_datetime(events_df["shift_start"], errors="coerce")
    events_df["shift_end"] = pd.to_datetime(events_df["shift_end"], errors="coerce")

    events_df["time"] = pd.to_datetime(events_df["time"], errors="coerce")
    events_df["year"] = events_df["time"].dt.year.astype(str)
    events_df["month"] = events_df["time"].dt.month.map(lambda x: f"{x:02d}")
    events_df["day"] = events_df["time"].dt.day.map(lambda x: f"{x:02d}")
    events_df["hour"] = events_df["time"].dt.hour.map(lambda x: f"{x:02d}")

    columns_to_write = [
        "time",
        "machine_id",
        "machine_name",
        "status_code",
        "no_of_stops",
        "event_duration",
        "factory_order",
        "part_number",
        "shift_start",
        "shift_end",
        "production_date",
        # Status code
        "code",
        "downtime_reason_minor_id",
        "downtime_reason_minor",
        "downtime_reason_major_id",
        "downtime_reason_major",
        "is_planned_downtime",
        "is_unplanned_downtime",
        "downtime_type",
        # Shift
        "shift_id",
        "shift_name",
        "shift_color",
        # Hierarchy
        "machine_group_child_id",
        "machine_group_child_name",
        "machine_group_parent_id",
        "machine_group_parent_name",
        "machine_group_grandparent_id",
        "machine_group_grandparent_name",
        "machine_group_great_grandparent_id",
        "machine_group_great_grandparent_name",
        "year",
        "month",
        "day",
        "hour",
    ]

    events_df = events_df.loc[:, columns_to_write].copy()

    # Exclude those running status code.
    events_df = events_df.loc[events_df["status_code"] != 100]

    wr.s3.to_parquet(
        df=events_df,
        path=s3_path,
        compression="snappy",
        dtype=downtime_schema,
        partition_cols=["machine_id", "year", "month", "day", "hour"],
        dataset=True,
        mode="overwrite_partitions",
    )
