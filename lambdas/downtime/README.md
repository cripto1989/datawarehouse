

## 1) Prerequisites

```bash
gimme-aws-creds --profile default
```

## 2) Docker Authentication

#### Ohio
```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.us-east-2.amazonaws.com

$VERSION = (Get-Content VERSION -Raw).Trim()

docker build --provenance=false -t bax-bxty-dm-nc-downtime:$VERSION .

docker tag bax-bxty-dm-nc-downtime:$VERSION 082347614916.dkr.ecr.us-east-2.amazonaws.com/bax-bxty-dm-nc-downtime:$VERSION

docker push 082347614916.dkr.ecr.us-east-2.amazonaws.com/bax-bxty-dm-nc-downtime:$VERSION
```


## 5) Deploy Lambda Function

```bash
aws lambda create-function --function-name bax-bxty-dm-nc-downtime --role arn:aws:iam::082347614916:role/bax-bxty-ncgai-1-service-role --code ImageUri=082347614916.dkr.ecr.us-east-2.amazonaws.com/bax-bxty-dm-nc-downtime:latest --timeout 600 --memory-size 128 --vpc-config SubnetIds=subnet-4ec4b635,subnet-b081b2d9,SecurityGroupIds=sg-05a04ffe66690a059 --region us-east-2 --package-type Image
```

## 6) Function Execution Payload

```json
{
    "events_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/raw/events/2026/07/01/raw_events_20260701_machines_84_85_86_87_155.jsonl",
    "machines_status_code_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_machines_status_code/machines_status_code.parquet",
    "shifts_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_shifts/shifts.parquet",
    "machines_groups_hierarchy_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_machines_groups_hierarchy/machines_groups_hierarchy.parquet",
    "s3_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/fact_downtime/"
}
```

## 7) Run the lambda

```sh
gimme-aws-creds --profile default

aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --invocation-type Event --cli-binary-format raw-in-base64-out --payload file://payload.json response.json
```

## 8) Amazon Athena

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS default.nc_downtime_events (
    `time` timestamp,
    `machine_name` string,
    `status_code` int,
    `no_of_stops` int,
    `event_duration` int,
    `factory_order` string,
    `part_number` string,
    `shift_start` timestamp,
    `shift_end` timestamp,
    `production_date` timestamp,
    `code` int,
    `downtime_reason_minor_id` int,
    `downtime_reason_minor` string,
    `downtime_reason_major_id` int,
    `downtime_reason_major` string,
    `is_planned_downtime` int,
    `is_unplanned_downtime` int,
    `downtime_type` string,
    `shift_id` int,
    `shift_name` string,
    `shift_color` string,
    `machine_group_child_id` int,
    `machine_group_child_name` string,
    `machine_group_parent_id` int,
    `machine_group_parent_name` string,
    `machine_group_grandparent_id` int,
    `machine_group_grandparent_name` string,
    `machine_group_great_grandparent_id` int,
    `machine_group_great_grandparent_name` string
)
PARTITIONED BY (
    `machine_id` int,
    `year` int,
    `month` int,
    `day` int,
    `hour` int
)
STORED AS PARQUET
LOCATION 's3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/fact_downtime/'
TBLPROPERTIES ("parquet.compress"="snappy");

MSCK REPAIR TABLE default.nc_downtime_events;
```

```sql
CREATE OR REPLACE VIEW nc_downtime_2026 AS
SELECT
    machine_id,
    machine_name,
    status_code,
    DATE(at_timezone(time, 'US/Eastern')) AS local_date,
    SUM(event_duration) AS downtime_duration,
    SUM(no_of_stops) AS no_of_stops,
    SUM(CASE WHEN status_code = 100 THEN event_duration ELSE 0 END) AS runtime_mins,
    part_number,
    factory_order,
    downtime_reason_minor,
    downtime_reason_major,
    downtime_type,
    DATE(at_timezone(production_date, 'US/Eastern')) AS production_date,
    is_planned_downtime,
    is_unplanned_downtime,
    shift_id,
    shift_name,
    shift_start,
    shift_end,
    shift_color,
    machine_group_child_id,
    machine_group_child_name,
    machine_group_parent_id,
    machine_group_parent_name,
    machine_group_grandparent_id,
    machine_group_grandparent_name,
    machine_group_great_grandparent_id,
    machine_group_great_grandparent_name,
    year,
    month,
    day
FROM nc_downtime_events
GROUP BY
    machine_id,
    machine_name,
    status_code,
    part_number,
    factory_order,
    downtime_reason_minor,
    downtime_reason_major,
    downtime_type,
    is_planned_downtime,
    is_unplanned_downtime,
    shift_id,
    shift_name,
    shift_start,
    shift_end,
    shift_color,
    machine_group_child_id,
    machine_group_child_name,
    machine_group_parent_id,
    machine_group_parent_name,
    machine_group_grandparent_id,
    machine_group_grandparent_name,
    machine_group_great_grandparent_id,
    machine_group_great_grandparent_name,
    year,
    month,
    day,
    date(at_timezone(time, 'US/Eastern')),
    DATE(at_timezone(production_date, 'US/Eastern'));
```
