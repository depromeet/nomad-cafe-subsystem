import requests

from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    core
)


class Ec2CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        userdata_file = open("./web_cdk/userdata.sh", "rb").read()
        userdata = ec2.UserData.for_linux()
        userdata.add_commands(str(userdata_file, 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "web_cdk-asg",
            vpc=props['vpc'],
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            key_name="yongho1037",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            user_data=userdata,
        )

        sg = ec2.SecurityGroup(
            self,
            id="web_cdk",
            vpc=props['vpc'],
            security_group_name="web_cdk"
        )

        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(f"{requests.get('https://api.ipify.org').text}/32"),
            connection=ec2.Port.tcp(22)
        )
