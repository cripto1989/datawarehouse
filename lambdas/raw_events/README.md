gimme-aws-creds --profile default

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 082347614916.dkr.ecr.eu-central-1.amazonaws.com

docker build --provenance=false -t bax-bxty-thf-datawarehouse-raw-events .

docker tag bax-bxty-thf-datawarehouse-raw-events:latest 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-raw-events:latest

docker push 082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-raw-events:latest


## 5) Deployment
```sh
aws lambda create-function --function-name bax-bxty-thf-raw-events --role arn:aws:iam::082347614916:role/bax-bxty-thfgai1-service-role --code ImageUri=082347614916.dkr.ecr.eu-central-1.amazonaws.com/bax-bxty-thf-datawarehouse-raw-events:latest --timeout 300 --memory-size 128 --environment "Variables={OPENSEARCH_ENDPOINT=vpc-baxaws-ops-prod-bxty-thr-os-ovowrsdta2dxcjeci63iai5ue4.eu-central-1.es.amazonaws.com,REGION=eu-central-1,OPENSEARCH_USERNAME=adminthf,OPENSEARCH_PASSWORD=3q-Zdy-deTRXYx4}" --vpc-config SubnetIds=subnet-3a2d0340,subnet-9e33dcf5,SecurityGroupIds=sg-047d115d81becb9c8 --region eu-central-1 --package-type Image
```

```json
{
  "start_time": "2026-06-25T23:00:00",
  "end_time": "2026-06-26T22:59:59",
  "index_name": "baxterity-production",
  "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"
}
```
