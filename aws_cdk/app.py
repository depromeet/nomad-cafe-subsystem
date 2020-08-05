#!/usr/bin/env python3

from aws_cdk import core

from web_cdk.vpc_cdk_stack import VpcCdkStack
from web_cdk.ec2_cdk_stack import Ec2CdkStack


base_props = {'Project': 'web_cdk'}
app = core.App()
vpc = VpcCdkStack(app, "VpcCdkStack", base_props)

ec2 = Ec2CdkStack(app, "Ec2CdkStack", vpc.outputs)
ec2.add_dependency(vpc)

app.synth()
