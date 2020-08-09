#!/bin/sh

yum update -y
yum install yum-utils python3 python3-pip python3-devel gcc httpd -y
pip3 install locust