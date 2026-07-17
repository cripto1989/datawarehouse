# BAX-BXTY-THF Datawarehouse - Raw Events Lambda

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
docker build --provenance=false -t bax-bxty-thf-datawarehouse-raw-events .
```

## 4) Tag and Push Docker Image

```bash
docker tag bax-bxty-thf-datawarehouse-raw-events:latest 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-raw-events

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-raw-events
```

## 5) Deploy Lambda Function

```bash
aws lambda create-function \
  --function-name bax-bxty-thf-raw-events \
  --role arn:aws:iam::082347614916:role/bax-bxty-thfgai1-service-role \
  --code ImageUri=082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-raw-events:latest \
  --timeout 300 \
  --memory-size 128 \
  --environment "Variables={OPENSEARCH_ENDPOINT=,REGION=,OPENSEARCH_USERNAME=,OPENSEARCH_PASSWORD=}" \
  --vpc-config SubnetIds=subnet-3a2d0340,subnet-9e33dcf5,SecurityGroupIds=sg-047d115d81becb9c8 \
  --region eu-central-1 \
  --package-type Image
```

## 6) Function Execution Payload

```json
{
  "start_time": "2026-06-25T23:00:00",
  "end_time": "2026-06-26T22:59:59",
  "index_name": "baxterity-production",
  "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"
}
```
