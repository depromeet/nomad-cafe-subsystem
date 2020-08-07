from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class VpcCdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        public_subnet = ec2.SubnetConfiguration(
            name="Public",
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24)
        private_subnet = ec2.SubnetConfiguration(
            name="Private",
            subnet_type=ec2.SubnetType.PRIVATE,
            cidr_mask=24)

        vpc = ec2.Vpc(self,
                      "web_cdk",
                      cidr="10.0.0.0/16",
                      enable_dns_hostnames=True,
                      enable_dns_support=True,
                      max_azs=2,
                      nat_gateway_provider=ec2.NatProvider.gateway(),   # NAT 구성 시 NAT gateway를 사용
                      nat_gateways=1,
                      subnet_configuration=[public_subnet, private_subnet]
                      )

        core.CfnOutput(self, "vpcid", value=vpc.vpc_id)

        self.output_props = props.copy()
        self.output_props['vpc'] = vpc
        self.output_props['subnets'] = vpc.public_subnets

    # property를 사용하면 변수 사용하듯이 메소드를 사용할 수 있음
    @property
    def outputs(self):
        return self.output_props
