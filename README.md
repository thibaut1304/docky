Creation clef ssh 
ssh-keygen -t rsa -b 4096 -f ~/.ssh/api-docker -N ""

sudo adduser --disabled-password --gecos "" api-docker
sudo mkdir -p /home/api-docker/.ssh
sudo vim /home/api-docker/.ssh/authorized_keys
sudo chown -R api-docker:api-docker /home/api-docker/.ssh
sudo chmod 700 /home/api-docker/.ssh
sudo chmod 600 /home/api-docker/.ssh/authorized_keys

sudo usermod -aG docker api-docker

ssh -i ~/.ssh/api-docker api-docker@192.168.x.x

