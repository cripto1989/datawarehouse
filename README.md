# Bxty ETL

This repository contains the ETL project for generating and publishing data to S3 in a Parquet-based layout, ready to be queried from Athena.

---

## 1) Docker build and publish

Use the commands below to build the container image, authenticate to Amazon ECR, and push the image.

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.eu-central-1.amazonaws.com

docker build --provenance=false -t bax-bxty-etl:1.43 .

docker tag bax-bxty-etl:1.43 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-etl:1.43

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-etl:1.43
```

> Note: make sure the image tag used in `docker build`, `docker tag`, and `docker push` matches your release version.

---

## 2) Athena / Glue table definition

Create the external table below to query the Parquet dataset stored in S3.

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS default.thf (
    `time` timestamp,
    `produced` int,
    `event_duration` int,
    `machine_name` string,
    `part_number` string,
    `production_target` double,
    `scrapped` int,
    `start_time` timestamp,
    `end_time` timestamp,
    `shift_start` timestamp,
    `shift_end` timestamp,
    `production_date` timestamp,
    `status_code` int,
    `ideal_cycle_time` double,
    `multiplier` int
)
PARTITIONED BY (
    `machine_id` int,
    `year` int,
    `month` int,
    `day` int
)
STORED AS PARQUET
LOCATION 's3://bax-bxty-thf-data-warehouse/warehouse/thf/'
TBLPROPERTIES ("parquet.compress"="snappy");

-- This scans all S3 paths and automatically registers partitions.
MSCK REPAIR TABLE default.thf;
```

```json
{
  "start_time": "2026-05-26T23:00:00",
  "end_time": "2026-05-27T22:59:59",
  "index_name": "<INDEX>",
  "save_to_s3": true,
  "s3_path": "s3://<PATH>/",
  "plant_prefix": "<PLANT_PREFIX>"
}
```

---

## 3) S3 data structure

The data is organized by plant and time partitioning. This layout helps Athena query the dataset efficiently.

```text
s3://bax-bxty-thf-data-warehouse/warehouse/thf//
├── machine_id=machine001/
│   ├── year=2024/
│   │   ├── month=01/
│   │   │   ├── day=15/
│   │   │   │   └── data.parquet  # All machines for this day
│   │   │   ├── day=16/
│   │   │   │   └── data.parquet
├── machine_id=machine002/
│   ├── year=2024/
│   │   ├── month=01/
│   │   │   ├── day=15/
│   │   │   │   └── data.parquet

s3://eu-west-1-data-warehouse-bucket/  # Different region, different bucket
├── machine_id=machine003/
│   ├── year=2024/
```

---

## 4) Project architecture

High-level flow of the project:

1. **Source / ingestion**: raw or transformed data is produced by the ETL process.
2. **Containerized ETL**: the application is packaged as a Docker image and pushed to Amazon ECR.
3. **Storage layer**: output data is written in **Parquet** format to Amazon S3.
4. **Query layer**: Athena uses the external table definition to query the data directly from S3.
5. **Partitioning strategy**: data is organized by `machine_id`, `year`, `month`, and `day` for better query performance.

You can expand this section later with diagrams, services, or environment-specific details.



## CHANGELOG

### 1.0.0 (2026-06-12)

#### Features (4 changes)

- [Feature 1](gitlab-org/gitlab@123abc) by @alice ([merge request](gitlab-org/gitlab!123))
- [Feature 2](gitlab-org/gitlab@456abc) ([merge request](gitlab-org/gitlab!456))
- [Feature 3](gitlab-org/gitlab@234abc) by @steve
- [Feature 4](gitlab-org/gitlab@456)
