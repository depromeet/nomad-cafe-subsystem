import boto3
import logging
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

conf = Config(region_name="ap-northeast-2")
ec2 = boto3.client('ec2', config=conf)
ssm = boto3.client('ssm', config=conf)


def lambda_handler(event, context):
    try:
        ec2_resp = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

        ec2_count = len(ec2_resp['Reservations'])
        if ec2_count == 0:
            logger.info('No EC2 is running')

        account = event["account"]
        repository_name = event["detail"]["repository-name"]
        # image_tag = event["detail"]["image-tag"]

        # 버전 체계 잡히기 전까지는 latest로 배포
        docker_image = f"{account}.dkr.ecr.ap-northeast-2.amazonaws.com/{repository_name}:latest"
        logger.info(docker_image)

        # Get All InstanceID
        instances = [i["InstanceId"] for r in ec2_resp["Reservations"] for i in r["Instances"]]
        logger.info(instances)
        ssm.send_command(
            InstanceIds=instances,
            DocumentName="AWS-RunShellScript",
            CloudWatchOutputConfig={
                "CloudWatchLogGroupName": "nomad-cafe-deploy",
                "CloudWatchOutputEnabled": True

            },
            Parameters={
                "commands": [
                    "aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS "
                    "--password-stdin 992189553983.dkr.ecr.ap-northeast-2.amazonaws.com",
                    "cd /home/ssm-user",
                    "docker-compose pull",
                    "docker-compose stop web",
                    "docker-compose rm web",
                    "docker-compose up -d"
                ],
                "executionTimeout": ["3600"]
            },
        )

    except Exception as e:
        logger.error(e)
        raise e
