#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart

from imports import k8s
# from .imports import k8s


class MyChart(Chart):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        label = {"app": "nomad-cafe"}

        k8s.Service(self, 'service',
                    spec=k8s.ServiceSpec(
                        type='NodePort',
                        ports=[k8s.ServicePort(
                            port=8000,
                            target_port=k8s.IntOrString.from_number(8000),
                            node_port=30001)],
                        selector=label))

        secret = k8s.Secret(self, 'secret',
                            type='Opaque',
                            string_data={
                                'DB_HOST': '',
                                'DB_NAME': 'nomad-cafe',
                                'DJANGO_ALLOWED_HOSTS': '*',
                                'DJANGO_DEBUG': 'True',
                                'DJANGO_SECRET_KEY': '',
                                'NEW_RELIC_LICENSE_KEY': '',
                            })

        k8s.Deployment(self, 'deployment',
                       spec=k8s.DeploymentSpec(
                           replicas=1,
                           selector=k8s.LabelSelector(match_labels=label),
                           template=k8s.PodTemplateSpec(
                               metadata=k8s.ObjectMeta(labels=label),
                               spec=k8s.PodSpec(containers=[
                                   k8s.Container(
                                       name='nomad-cafe',
                                       image='354304228313.dkr.ecr.ap-northeast-2.amazonaws.com/nomad-cafe',
                                       image_pull_policy="Always",
                                       ports=[k8s.ContainerPort(container_port=8000)],
                                       command=["gunicorn", "was.wsgi:application", "--bind", "0.0.0.0:8000"],
                                       env_from=[k8s.EnvFromSource(secret_ref=k8s.SecretEnvSource(name=secret.name))],
                                       resources=k8s.ResourceRequirements(
                                           requests={
                                               "cpu": k8s.Quantity.from_string("100m"),
                                               "memory": k8s.Quantity.from_string("128Mi")
                                           },
                                           limits={
                                               "cpu": k8s.Quantity.from_string("200m"),
                                               "memory": k8s.Quantity.from_string("256Mi")
                                           }
                                       )
                                   )]))))



app = App()
MyChart(app, "nomad_cafe")

app.synth()
