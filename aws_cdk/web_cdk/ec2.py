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
        self.create_role()
        self.create_nlb(props)
        self.create_asg(service_type)

    def create_role(self):
        if "default_role" not in self.output_props:
            default_role = iam.Role(
                self,
                "DefaultRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            )
            default_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
            self.output_props["default_role"] = default_role

    def create_nlb(self, props):
        if "nlb" not in self.output_props:
            nlb = lb.NetworkLoadBalancer(self, id="nlb_cdk",
                                         vpc=props['vpc'],
                                         internet_facing=True,
                                         cross_zone_enabled=True,
                                         vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))

            self.output_props["nlb"] = nlb

    def create_asg(self, service_type):
        if service_type == "web":
            self.create_asg_by_service(name=service_type,
                                       userdata_path="./web_cdk/userdata_web.sh",
                                       key_name="yongho1037",
                                       port=80)
        elif service_type == "stress_test":
            self.create_asg_by_service(name=service_type,
                                       userdata_path="./web_cdk/userdata_stress_test.sh",
                                       key_name="yongho1037",
                                       port=8089)
        else:
            raise Exception("invalid service type. ", service_type)

    def create_asg_by_service(self, name, userdata_path, key_name, port):
        role = self.output_props["default_role"]
        sg = self.output_props["sg"]
        nlb = self.output_props["nlb"]
        userdata = ec2.UserData.for_linux()
        with open(userdata_path, "rb") as f:
            userdata.add_commands(str(f.read(), 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            name,
            vpc=self.output_props['vpc'],
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            key_name=key_name,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            user_data=userdata,
            security_group=sg,
            spot_price="0.005",
            min_capacity=1,
            max_capacity=3,
            desired_capacity=1,
            role=role,
        )

        nlb.add_listener(name, port=port, protocol=lb.Protocol.TCP) \
            .add_targets(name, port=port, targets=[asg])

    @property
    def outputs(self):
        return self.output_props
