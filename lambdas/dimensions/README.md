# BAX-BXTY-THF Datawarehouse - Dimensions Lambda

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
docker build --provenance=false -t bax-bxty-thf-datawarehouse-dimensions .
```

## 4) Tag and Push Docker Image

```bash
docker tag bax-bxty-thf-datawarehouse-dimensions:latest 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-dimensions:latest

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-dimensions:latest
```

## 5) Deploy Lambda Function

```bash
aws lambda create-function \
  --function-name bax-bxty-thf-dimensions \
  --role arn:aws:iam::082347614916:role/bax-bxty-thfgai1-service-role \
  --code ImageUri=082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-dimensions:latest \
  --timeout 60 \
  --memory-size 128 \
  --environment "Variables={DB_HOST=,DB_USER=,DB_PASSWORD=,DB_NAME=}" \
  --vpc-config SubnetIds=subnet-3a2d0340,subnet-9e33dcf5,SecurityGroupIds=sg-047d115d81becb9c8 \
  --region eu-central-1 \
  --package-type Image
```

## 6) Function Execution Payload

```json
{
  "queries": [
    {
      "query": "SELECT * FROM machine_partconfiguration pc INNER JOIN machine_part p ON pc.part_id = p.id;",
      "path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/curated/dim_part_configurations/part_configuration.parquet"
    },
    {
      "query": "SELECT * FROM machine_statuscode sc INNER JOIN machine_status s ON sc.status_id = s.id ORDER BY sc.code;",
      "path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/curated/dim_machines_status_code/machines_status_code.parquet"
    }
  ]
}
```

## 7) Reference: Hive External Table

```sql
CREATE EXTERNAL TABLE part_configuration (
    id BIGINT,
    seconds_per_part DOUBLE,
    machine_id BIGINT,
    part_id DOUBLE,
    conversion_cost DOUBLE,
    material_cost DOUBLE,
    seconds_per_part_2 DOUBLE,
    multiplier DOUBLE
)
STORED AS PARQUET
LOCATION 's3://bax-bxty-thf-data-warehouse/warehouse/thf/dim_part_configuration/part_configuration.parquet'
```
