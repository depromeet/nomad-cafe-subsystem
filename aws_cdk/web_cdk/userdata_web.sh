#!/bin/sh
# 테스트를 위한 샘플 코드

yum update -y

# install docker
amazon-linux-extras install -y docker
service docker start
usermod -a -G docker ec2-user
usermod -a -G docker ssm-user
chkconfig docker on
curl -L https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# install aws cli v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# install httpd
yum install httpd -y
systemctl enable httpd
systemctl start httpd
echo "<html><head><title> Example Web Server</title></head>" >  /var/www/html/index.html
echo "<body>" >>  /var/www/html/index.html
echo "<div><center><h2>Welcome AWS $(hostname -f) </h2>" >>  /var/www/html/index.html
echo "<hr/>" >>  /var/www/html/index.html
curl http://169.254.169.254/latest/meta-data/instance-id >> /var/www/html/index.html
echo "</center></div></body></html>" >>  /var/www/html/index.html