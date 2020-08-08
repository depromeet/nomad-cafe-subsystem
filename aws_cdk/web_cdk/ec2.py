from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as lb,
    aws_autoscaling as autoscaling,
    core
)


class Ec2CdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, service_type: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.output_props = props.copy()
        if "default_role" not in self.output_props:
            default_role = iam.Role(
                self,
                "DefaultRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            )
            default_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
            self.output_props["default_role"] = default_role

        if "nlb" not in self.output_props:
            nlb = lb.NetworkLoadBalancer(self, id="nlb_cdk",
                                         vpc=props['vpc'],
                                         internet_facing=True,
                                         cross_zone_enabled=True,
                                         vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))

            self.output_props["nlb"] = nlb

        if service_type == "web":
            self.web()
        elif service_type == "stress_test":
            self.stress_test()

    def web(self):
        role = self.output_props["default_role"]
        sg = self.output_props["sg"]
        nlb = self.output_props["nlb"]
        userdata = ec2.UserData.for_linux()
        with open("./web_cdk/userdata_web.sh", "rb") as f:
            userdata.add_commands(str(f.read(), 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "web",
            vpc=self.output_props['vpc'],
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            key_name="yongho1037",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            user_data=userdata,
            security_group=sg,
            spot_price="0.005",
            min_capacity=1,
            max_capacity=3,
            desired_capacity=1,
            role=role,
        )

        nlb.add_listener("web", port=80, protocol=lb.Protocol.TCP) \
            .add_targets("web", port=80, targets=[asg])

        return asg

    def stress_test(self):
        role = self.output_props["default_role"]
        sg = self.output_props["sg"]
        nlb = self.output_props["nlb"]
        userdata = ec2.UserData.for_linux()
        with open("./web_cdk/userdata_stress_test.sh", "rb") as f:
            userdata.add_commands(str(f.read(), 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "stress-test",
            vpc=self.output_props['vpc'],
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            key_name="yongho1037",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            user_data=userdata,
            security_group=sg,
            spot_price="0.005",
            min_capacity=1,
            max_capacity=3,
            desired_capacity=1,
            role=role,
        )

        nlb.add_listener("locust", port=8089, protocol=lb.Protocol.TCP) \
            .add_targets("locust", port=8089, targets=[asg])

        return asg

    @property
    def outputs(self):
        return self.output_props
