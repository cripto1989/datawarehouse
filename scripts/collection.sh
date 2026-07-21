#!/bin/bash
set -e

export AWS_CLI_BINARY_FORMAT=raw-in-base64-out

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-01T23:00:00 to 2026-05-02T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --payload '{"start_time": "2026-05-01T23:00:00", "end_time": "2026-05-02T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-02T23:00:00 to 2026-05-03T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-02T23:00:00", "end_time": "2026-05-03T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-03T23:00:00 to 2026-05-04T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-03T23:00:00", "end_time": "2026-05-04T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-04T23:00:00 to 2026-05-05T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-04T23:00:00", "end_time": "2026-05-05T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-05T23:00:00 to 2026-05-06T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-05T23:00:00", "end_time": "2026-05-06T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-06T23:00:00 to 2026-05-07T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-06T23:00:00", "end_time": "2026-05-07T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-07T23:00:00 to 2026-05-08T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-07T23:00:00", "end_time": "2026-05-08T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-08T23:00:00 to 2026-05-09T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-08T23:00:00", "end_time": "2026-05-09T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-09T23:00:00 to 2026-05-10T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-09T23:00:00", "end_time": "2026-05-10T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-10T23:00:00 to 2026-05-11T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-10T23:00:00", "end_time": "2026-05-11T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-11T23:00:00 to 2026-05-12T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-11T23:00:00", "end_time": "2026-05-12T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-12T23:00:00 to 2026-05-13T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-12T23:00:00", "end_time": "2026-05-13T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-13T23:00:00 to 2026-05-14T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-13T23:00:00", "end_time": "2026-05-14T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-14T23:00:00 to 2026-05-15T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-14T23:00:00", "end_time": "2026-05-15T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-15T23:00:00 to 2026-05-16T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-15T23:00:00", "end_time": "2026-05-16T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-16T23:00:00 to 2026-05-17T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-16T23:00:00", "end_time": "2026-05-17T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-17T23:00:00 to 2026-05-18T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-17T23:00:00", "end_time": "2026-05-18T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-18T23:00:00 to 2026-05-19T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-18T23:00:00", "end_time": "2026-05-19T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-19T23:00:00 to 2026-05-20T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-19T23:00:00", "end_time": "2026-05-20T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-20T23:00:00 to 2026-05-21T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-20T23:00:00", "end_time": "2026-05-21T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-21T23:00:00 to 2026-05-22T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-21T23:00:00", "end_time": "2026-05-22T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-22T23:00:00 to 2026-05-23T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-22T23:00:00", "end_time": "2026-05-23T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-23T23:00:00 to 2026-05-24T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-23T23:00:00", "end_time": "2026-05-24T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-24T23:00:00 to 2026-05-25T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-24T23:00:00", "end_time": "2026-05-25T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-25T23:00:00 to 2026-05-26T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-25T23:00:00", "end_time": "2026-05-26T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-26T23:00:00 to 2026-05-27T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-26T23:00:00", "end_time": "2026-05-27T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-27T23:00:00 to 2026-05-28T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-27T23:00:00", "end_time": "2026-05-28T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-28T23:00:00 to 2026-05-29T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-28T23:00:00", "end_time": "2026-05-29T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-29T23:00:00 to 2026-05-30T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-29T23:00:00", "end_time": "2026-05-30T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-30T23:00:00 to 2026-05-31T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-30T23:00:00", "end_time": "2026-05-31T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1

# echo "Invoking Lambda function to collect THF raw events data from 2026-05-31T23:00:00 to 2026-06-01T22:59:59"
# aws lambda invoke --function-name bax-bxty-thf-raw-events --region eu-central-1 --cli-binary-format raw-in-base64-out --invocation-type Event --payload '{"start_time": "2026-05-31T23:00:00", "end_time": "2026-06-01T22:59:59", "index_name": "baxterity-production", "s3_path": "s3://bax-bxty-thf-data-warehouse/warehouse/thf/raw/events/"}' response.json >/dev/null 2>&1
