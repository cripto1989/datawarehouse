gimme-aws-creds --profile default

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.eu-central-1.amazonaws.com

docker build --provenance=false -t bax-bxty-thf-datawarehouse-dimensions .

docker tag bax-bxty-thf-datawarehouse-dimensions:latest 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-dimensions:latest

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-dimensions:latest


## 5) Deployment
```sh

aws lambda create-function --function-name bax-bxty-thf-dimensions --role arn:aws:iam::082347614916:role/bax-bxty-thfgai1-service-role --code ImageUri=082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-dimensions:latest --timeout 60 --memory-size 128 --environment "Variables={DB_HOST=,DB_USER=,DB_PASSWORD=,DB_NAME=}" --vpc-config SubnetIds=subnet-3a2d0340,subnet-9e33dcf5,SecurityGroupIds=sg-047d115d81becb9c8 --region eu-central-1 --package-type Image
```

{
  "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/dim_part_configuration"
}

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
