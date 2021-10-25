yum update -y && yum install epel-release rpm-build rpmdevtools psmisc nano ntp wget -y
sleep 5s
systemctl enable ntpd && systemctl start ntpd && timedatectl set-timezone Asia/Kuala_Lumpur
sleep 5s
wget https://github.com/jmdaweb/NVDARemoteServer/releases/download/release-1.9/NVDARemoteServer-1.9-1.el7.noarch.rpm && rpm -U NVDARemoteServer-1.9-1.el7.noarch.rpm && NVDARemoteCertificate && nano /etc/systemd/system/multi-user.target.wants/NVDARemoteServer.service && systemctl daemon-reload && NVDARemoteServer restart
sleep 5s
dd if=/dev/zero of=/swapfile bs=16384 count=1048576 && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile && echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
sleep 5s
useradd tt && mkdir /home/tt/data /home/tt/log /home/tt/xml && mv tt5srv /home/tt5srv && mv 2005-2005/tt5srv.xml /home/tt/xml/tt5srv.xml && mv 2005-2005/tt.service /lib/systemd/system/tt.service && chmod 775 /home/tt5srv && chown -R tt:tt /home/tt/* && chmod -R 775 /home/tt/* && systemctl enable tt.service
sleep 5s
echo "Complete!"