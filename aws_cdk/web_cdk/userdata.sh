#!/bin/sh
# 테스트를 위한 샘플 코드

yum update -y
yum install yum-utils python3 python3-pip python3-devel gcc httpd -y
pip3 install locust

#enable and start httpd
systemctl enable httpd
systemctl start httpd
echo "<html><head><title> Example Web Server</title></head>" >  /var/www/html/index.html
echo "<body>" >>  /var/www/html/index.html
echo "<div><center><h2>Welcome AWS $(hostname -f) </h2>" >>  /var/www/html/index.html
echo "<hr/>" >>  /var/www/html/index.html
curl http://169.254.169.254/latest/meta-data/instance-id >> /var/www/html/index.html
echo "</center></div></body></html>" >>  /var/www/html/index.html