from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as lb,
    aws_autoscaling as autoscaling,
    core
)


class Ec2CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        userdata = ec2.UserData.for_linux()
        with open("./web_cdk/userdata.sh", "rb") as f:
            userdata.add_commands(str(f.read(), 'utf-8'))

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
            security_group=props["sg"],
        )

        nlb = lb.NetworkLoadBalancer(self, id="nlb_cdk",
                                     vpc=props['vpc'],
                                     internet_facing=True,
                                     cross_zone_enabled=True,
                                     vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))
        listener = nlb.add_listener("web_listener", port=80, protocol=lb.Protocol.TCP)
        listener.add_targets("web_target", port=80, targets=[asg])

        self.output_props = props.copy()
        self.output_props['asg'] = asg

    # property를 사용하면 변수 사용하듯이 메소드를 사용할 수 있음
    @property
    def outputs(self):
        return self.output_props
