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

        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(f"{requests.get('https://api.ipify.org').text}/32"),
            connection=ec2.Port.tcp(22)
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(f"{requests.get('https://api.ipify.org').text}/32"),
            connection=ec2.Port.tcp(80)
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4("10.0.0.0/16"),
            connection=ec2.Port.tcp(80)
        )

        self.output_props = props.copy()
        self.output_props['sg'] = sg

    # property를 사용하면 변수 사용하듯이 메소드를 사용할 수 있음
    @property
    def outputs(self):
        return self.output_props
