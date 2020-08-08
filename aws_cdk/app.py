#!/usr/bin/env python3

from web_cdk.ec2 import Ec2CdkStack
from web_cdk.security_group import SgCdkStack
from web_cdk.vpc import VpcCdkStack

from aws_cdk import core

base_props = {'Project': 'web_cdk'}
app = core.App()
vpc = VpcCdkStack(app, "VpcCdkStack", base_props)

sg = SgCdkStack(app, "SgCdkStack", vpc.outputs)
sg.add_dependency(vpc)

ec2_web = Ec2CdkStack(app, "WebCdkStack", "web", sg.outputs)
ec2_web.add_dependency(sg)

ec2_stress_test = Ec2CdkStack(app, "StressTestCdkStack", "stress_test", ec2_web.outputs)
ec2_stress_test.add_dependency(ec2_web)

app.synth()
