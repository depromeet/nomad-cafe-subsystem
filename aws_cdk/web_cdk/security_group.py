import requests

from aws_cdk import (
    aws_ec2 as ec2,
    core
)


class SgCdkStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        sg = ec2.SecurityGroup(
            self,
            id="web_cdk",
            vpc=props['vpc'],
            security_group_name="web_cdk"
        )

        my_ip = f"{requests.get('https://api.ipify.org').text}/32"
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(my_ip),
            connection=ec2.Port.tcp(22)
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(my_ip),
            connection=ec2.Port.tcp(80)
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(my_ip),
            connection=ec2.Port.tcp(8089)
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(80)
        )

        self.output_props = props.copy()
        self.output_props['sg'] = sg

    @property
    def outputs(self):
        return self.output_props
