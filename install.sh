#!/bin/bash
sudo apt-get update -y
sudo apt-get upgrade -y
sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    oracle-java8-installer -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce
USER = whoami
sudo usermod -aG docker $USER
wget http://mirror.fibergrid.in/apache/kafka/0.10.0.1/kafka_2.10-0.10.0.1.tgz
mkdir ~/kafka
sudo tar -xvf kafka_2.10-0.10.0.1.tgz -C ~/
mv kafka_2.10-0.10.0.1 kafka
