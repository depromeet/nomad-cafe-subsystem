#!/usr/bin/env python3

from web_cdk.ec2_cdk_stack import Ec2CdkStack
from web_cdk.sg_cdk_stack import SgCdkStack
from web_cdk.vpc_cdk_stack import VpcCdkStack

from aws_cdk import core

base_props = {'Project': 'web_cdk'}
app = core.App()
vpc = VpcCdkStack(app, "VpcCdkStack", base_props)

sg = SgCdkStack(app, "SgCdkStack", vpc.outputs)
sg.add_dependency(vpc)

ec2 = Ec2CdkStack(app, "Ec2CdkStack", sg.outputs)
ec2.add_dependency(sg)

app.synth()
