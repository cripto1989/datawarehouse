# BAX-BXTY-THF Datawarehouse - ETL

## 1) Prerequisites

```bash
gimme-aws-creds --profile default
```

## 2) Docker Authentication

```sh
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.us-east-2.amazonaws.com
```

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.eu-central-1.amazonaws.com
```

## 3) Build Docker Image

```sh
docker build --provenance=false -t bax-bxty-dm-nc-etl .
```

```bash
docker build --provenance=false -t bax-bxty-etl .
```

## 4) Tag and Push Docker Image

```sh
docker tag bax-bxty-dm-nc-etl:latest 082347614916.dkr.ecr.us-east-2.amazonaws.com/bax-bxty-dm-nc-etl:latest

docker push 082347614916.dkr.ecr.us-east-2.amazonaws.com/bax-bxty-dm-nc-etl:latest
```

```bash
docker tag bax-bxty-etl 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-etl

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-etl
```

## 5) Deploy Lambda Function

```sh
aws lambda create-function
  --function-name bax-bxty-dm-nc-etl
  --role arn:aws:iam::082347614916:role/bax-bxty-ncgai-1-service-role
  --code ImageUri=082347614916.dkr.ecr.us-east-2.amazonaws.com/bax-bxty-dm-nc-etl:latest
  --timeout 900
  --memory-size 4096
  --vpc-config SubnetIds=subnet-4ec4b635,subnet-b081b2d9,SecurityGroupIds=sg-05a04ffe66690a059
  --region us-east-2
  --package-type Image
```

## 6) Function Execution Payload

```json
{
    "local_timezone": "US/Easter",
    "save_to_s3": true,
    "events_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/raw/events/2026/07/01/raw_events_20260701_machines_84_85_86_87_88_89_90_91_92_93.jsonl",
    "part_configuration_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_part_configurations/part_configuration.parquet",
    "machine_status_code_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/dim_machines_status_code/machines_status_code.parquet",
    "s3_output_path": "s3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/fact_events/"
}
```

```json
{
    "local_timezone": "Europe/London",
    "save_to_s3": true,
    "events_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/raw_events_20260701.jsonl",
    "part_configuration_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/curated/dim_part_configurations/part_configuration.parquet",
    "machine_status_code_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/curated/dim_machines_status_code/machines_status_code.parquet",
    "s3_output_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/curated/fact_events/"
}
```

## 7) Amazon Athena Tables

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS default.nc_fact_events (
    `time` timestamp,
    `produced` int,
    `event_duration` int,
    `machine_name` string,
    `part_number` string,
    `production_target` double,
    `scrapped` int,
    `start_time` timestamp,
    `end_time` timestamp,
    `shift_id` int,
    `shift_start` timestamp,
    `shift_end` timestamp,
    `production_date` timestamp,
    `status_code` int,
    `ideal_cycle_time` double,
    `multiplier` int,
    `unplanned_down` int,
    `planned_down` int,
    `factory_order` string
)
PARTITIONED BY (
    `machine_id` int,
    `year` int,
    `month` int,
    `day` int,
    `hour` int
)
STORED AS PARQUET
LOCATION 's3://bax-bxty-dm-nc-data-warehouse/warehouse/nc/curated/fact_events/'
TBLPROPERTIES ("parquet.compress"="snappy");

MSCK REPAIR TABLE default.nc_fact_events;
```

## 7) Amazon Athena Views

```sql
CREATE OR REPLACE VIEW events_2026_07 AS
with events as (select
    machine_id,
    machine_name,
    date(at_timezone(time, 'Europe/London')) as local_date,
    sum(scrapped) as scrap_pcs,
    sum(production_target) as target_qty,
    sum(case when unplanned_down = 1 then event_duration else 0 end) as unplanned_downtime_min,
    sum(produced) produced_qty,
    sum((3600 / ideal_cycle_time) * multiplier) as ideal_uph,
    sum(case when planned_down = 1 then event_duration else 0 end) as planned_downtime_min,
    sum(case when status_code = 100 then event_duration else 0 end) as runtime_mins,
    sum(event_duration) as duration_time,
    factory_order,
    part_number,
    shift_id,
    year,
    month,
    day
from fact_events
where machine_id>0
group by machine_id, machine_name, factory_order, part_number, shift_id, year, month, day, date(at_timezone(time, 'Europe/London')))
select
    events.machine_id,
    machine_name,
    local_date,
    scrap_pcs,
    part_number,
    target_qty,
    unplanned_downtime_min,
    produced_qty,
    ideal_uph,
    planned_downtime_min,
    runtime_mins,
    duration_time,
    factory_order,
    shift_id,
    name as shift_name,
    color as shift_color,
    machine_group_child_id,
    machine_group_child_name,
    machine_group_parent_id,
    machine_group_parent_name,
    machine_group_grandparent_id,
    machine_group_grandparent_name,
    machine_group_great_grandparent_id,
    machine_group_great_grandparent_name,
    events.year as year,
    events.month as month,
    events.day as day
from events
inner join (select id, name, color from dim_shifts) as s on events.shift_id = s.id
inner join machines_groups_hierarchy as mgh on events.machine_id=mgh.machine_id;
```

## 7) Run the lambda

```sh
gimme-aws-creds --profile default

aws lambda invoke --function-name bax-bxty-thf-etl --region eu-central-1 --invocation-type Event --cli-binary-format raw-in-base64-out --payload file://payload.json response.json
```
