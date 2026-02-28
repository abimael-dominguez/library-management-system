#!/bin/bash
set -e

# 1) Remove conflicting packages
sudo apt-get update
sudo apt-get upgrade
sudo apt-get remove -y docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc || true

# 2) Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg unzip

# 3) Add Docker's official GPG key and repository
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4) Install Docker Engine + Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5) Enable and start services
sudo systemctl unmask docker.service docker.socket || true
sudo rm -rf /etc/systemd/system/docker.service.d
sudo systemctl daemon-reload
sudo systemctl enable --now containerd docker.socket docker
sudo systemctl restart docker

# 6) Optional: run docker without sudo
sudo usermod -aG docker $USER
newgrp docker

# If daemon is not running:
sudo systemctl start docker

# 7) Verify Docker installation
docker --version
docker compose version
docker run --rm hello-world

# Install AWS CLI v2
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    AWSCLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
else
    AWSCLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
fi

curl "$AWSCLI_URL" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install --update

# Verify AWS CLI installation
aws --version
