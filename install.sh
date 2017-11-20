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
sudo apt-get install docker-ce docker-compose -y
sudo usermod -aG docker $USER
wget http://apache.mirrors.spacedump.net/kafka/1.0.0/kafka_2.12-1.0.0.tgz 
sudo tar -xvf kafka_2.12-1.0.0.tgz -C ~/
mv kafka_2.12-1.0.0 kafka
