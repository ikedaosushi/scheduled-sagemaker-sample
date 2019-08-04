import os
import json
import boto3

CLUSTER_NAME = os.environ["CLUSTER_NAME"]
TASK_DEFINITION = os.environ["TASK_DEFINITION"]
ECS_CONTAINER_NAME = os.environ["ECS_CONTAINER_NAME"]
REGION_NAME = os.environ["REGION_NAME"]
SUBNET_IDS = os.environ["SUBNET_IDS"]

CONTAINER_ENV = {
    "S3_BUCKET": os.environ["S3_BUCKET"],
    "SM_ROLE": os.environ["SM_ROLE"],
    "REGION_NAME": os.environ["REGION_NAME"],
    "DEPLOY_ENDPOINT_NAME": os.environ["DEPLOY_ENDPOINT_NAME"]
}

def train(event, context):
    fargate = boto3.client("ecs", region_name=REGION_NAME)
    resp = fargate.run_task(
        cluster=CLUSTER_NAME,
        taskDefinition=TASK_DEFINITION,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': SUBNET_IDS.split(",")
                , 'assignPublicIp': 'ENABLED'
            }
        },
        overrides={
            "containerOverrides": [
                {
                    'name': ECS_CONTAINER_NAME,
                    'environment': [
                        {"name": k, "value": v} for k, v in CONTAINER_ENV.items()
                    ]
                }
            ]
        }
    )

    url_base = "https://ap-northeast-1.console.aws.amazon.com/ecs/home?region=ap-northeast-1#/clusters/"
    cluster_name = CLUSTER_NAME
    task_id = resp['tasks'][0]['taskArn'].split("/")[-1]
    url = url_base + cluster_name + "/tasks/" + task_id + "/details"
    message = f"In order to check task, go to {url}"

    return {
        "ok": True, "message": message
    }

def check(event, context):
    return {
        "CLUSTER": CLUSTER_NAME,
        "TASK_DEFINITION": TASK_DEFINITION,
        "ECS_CONTAINER_NAME": ECS_CONTAINER_NAME,
        "CONTAINER_ENV": CONTAINER_ENV,
        "REGION_NAME": REGION_NAME,
        "SUBNET_IDS": SUBNET_IDS.split(",")
    }
