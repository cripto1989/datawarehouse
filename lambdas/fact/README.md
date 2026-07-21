# BAX-BXTY-THF Datawarehouse - ETL

## 1) Prerequisites

```bash
gimme-aws-creds --profile default
```

## 2) Docker Authentication

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.eu-central-1.amazonaws.com
```

## 3) Build Docker Image

```bash
docker build --provenance=false -t bax-bxty-etl .
```

## 4) Tag and Push Docker Image

```bash
docker tag bax-bxty-etl 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-etl

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-etl
```

## 6) Function Execution Payload

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
CREATE EXTERNAL TABLE IF NOT EXISTS default.fact_events (
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
LOCATION 's3://bax-bxty-thf-data-warehouse/warehouse/thf/curated/fact_events/'
TBLPROPERTIES ("parquet.compress"="snappy");

MSCK REPAIR TABLE default.fact_events;
```

## 7) Amazon Athena Views

```sql
CREATE OR REPLACE VIEW events_2026_07 AS
with events as (select
    machine_id,
    machine_name,
    date(at_timezone(time, 'Europe/London')) as local_time,
    sum(scrapped) as scrap_pcs,
    sum(production_target) as target_qty,
    sum(case when unplanned_down = 1 then event_duration else 0 end) as unplanned_downtime_min,
    sum(produced) produced_qtya,
    sum((3600 / ideal_cycle_time) * multiplier) as ideal_uph,
    sum(case when planned_down = 1 then event_duration else 0 end) as planned_downtime_min,
    sum(case when status_code = 100 then event_duration else 0 end) as runtime_mins,
    sum(event_duration) as duration_time,
    factory_order,
    shift_id
from fact_events
where machine_id>0
group by machine_id, machine_name, factory_order, shift_id, date(at_timezone(time, 'Europe/London')))
select
*
from events
inner join (select id, name, color from dim_shifts) as s on events.shift_id = s.id
inner join machines_groups_hierarchy as mgh on events.machine_id=mgh.machine_id;
```

## 7) Run the lambda

```sh
gimme-aws-creds --profile default

aws lambda invoke --function-name bax-bxty-thf-etl --region eu-central-1 --invocation-type Event --cli-binary-format raw-in-base64-out --payload file://payload.json response.json
```
