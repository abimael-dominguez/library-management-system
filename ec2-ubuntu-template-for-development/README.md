# Ubuntu EC2 Setup: Docker, Docker Compose, and AWS CLI

> Verified working on: 2026-02-27
## Install Docker Engine and Docker Compose Plugin

```bash
set -e

# 1) Remove conflicting packages
sudo apt-get update
sudo apt-get upgrade
sudo apt-get remove -y docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc || true

# 2) Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

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

# 7) Verify
docker --version
docker compose version
docker run --rm hello-world
```

## Install AWS CLI v2

```bash
set -e

# 1) Prerequisites
sudo apt-get update
sudo apt-get install -y curl unzip

# 2) Download installer (x86_64)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# If your instance is ARM/Graviton, use this instead:
# curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"

# 3) Install
unzip -q awscliv2.zip
sudo ./aws/install --update

# 4) Verify
aws --version
```

## Configure AWS credentials

```bash

# Named profile (immersion profile for this project)
aws configure --profile <your-profile>

Other Optional commands
      # Access key profile
      aws configure

      # SSO profile
      aws configure sso
      aws sso login --profile <your-profile>
```

## Verification

- System dependencies for local development (run once):
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker

  # if the Docker daemon is not running:
  sudo systemctl start docker

  sudo apt-get upgrade
  sudo apt update
  sudo apt install -y zip unzip curl

  PY_MM=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  sudo apt update
  sudo apt install -y "python${PY_MM}-venv" || sudo apt install -y python3-venv
  ```
  For a tighter command, you can substitute the last block with:
  ```bash
  sudo apt update
  sudo apt install -y "python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')-venv"
  ```

## SSH Setup

### Secure SSH permissions

1. Apply the required permissions so SSH and the private key stay locked down:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/config
   chmod 400 /home/abimael/Desktop/secrets/ec2/account_894064921954/ec2-ubuntu-ssh-key-pair.pem
   ```
2. Confirm the resulting bits match expectations:
   ```
   ~/.ssh -> drwx------
   ~/.ssh/config -> -rw-------
   /home/abimael/Desktop/secrets/ec2/account_894064921954/ec2-ubuntu-ssh-key-pair.pem -> -r--------
   ```

### VS Code Remote SSH

1. Install the **Remote - SSH** extension in VS Code.
2. Open the command palette again (`Ctrl+P`) and run `Remote-SSH: Connect to Host…`.
  - Configure Host --> /home/<user>/.ssh/config
3. When prompted, select or paste the host definition below.

```text
Host <EC2 Name>
    HostName <EC2 public DNS>
    User <user> # ubuntu
    IdentityFile </path/to/file.pem>
```

5. Open the command palette again (`Ctrl+P`) and run `Remote-SSH: Connect to Host…`.
  - Follow the prompts to accept the host key and open a remote window.
