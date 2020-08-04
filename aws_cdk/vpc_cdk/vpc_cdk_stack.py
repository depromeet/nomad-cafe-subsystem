from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class VpcCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "nomad-cafe",
                      cidr="10.0.0.0/16",
                      max_azs=4
                      )
