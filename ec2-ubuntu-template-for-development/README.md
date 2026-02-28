# Ubuntu EC2 Setup: Docker, Docker Compose, and AWS CLI


## Prerequisites


Open the AWS Console, go to the EC2 service, and create a key pair:

```bash
ec2-ubuntu-ssh-key-pair
```

Download the .csv file; you will use it later to connect to the EC2 instance from your local computer.

- Open the ```ec2-ubuntu-template-for-development/ec2-ubuntu-ssh.yml``` and veryfy the parameters are valid and updated.

- Deploy the stack using the AWS Console. Recommendation: set ```ProjectName``` as your CloudFormation Stack Name. You can see the ```ProjectName``` in ```ec2-ubuntu-ssh.yml```

## SSH Setup

### Secure SSH permissions

1. Apply the required permissions so SSH and the private key stay locked down:
   ```bash
   chmod 400 /path/to/key-pair-file.pem
   chmod 700 ~/.ssh         # optional
   chmod 600 ~/.ssh/config  # optional
   ```
2. Confirm the resulting bits match expectations:
   ```
   ls -ld </path/to/key-pair-file.pem>  -> -r--------
   ls -ld ~/.ssh                        -> drwx------
   ls -ld ~/.ssh/config                 -> -rw-------
   ```

### VS Code Remote SSH

1. Install the **Remote - SSH** extension in VS Code.
2. Open the command palette again (`Ctrl+P`) and run `Remote-SSH: Connect to Host…`.
  - Configure Host --> `/home/<user>/.ssh/config`
3. It will open the `~/.ssh/config ` file; paste the host definition below:

```bash
Host <EC2 Name>
    HostName <EC2 public DNS>
    User <user> # ubuntu
    IdentityFile </path/to/key-pair-file.pem>
```

After updating the parameters save the file.

4. Open the command palette again (`Ctrl+P`) and run `Remote-SSH: Connect to Host…`.
  - Follow the prompts to accept the host key and open a remote window.


## Install Docker Engine and Docker Compose Plugin (in the EC2)
> Verified working on: 2026-02-27

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
sudo usermod -aG docker ubuntu
newgrp docker

# If daemon is not running:
sudo systemctl start docker

# 7) Verify
docker --version
docker compose version
docker run --rm hello-world
```

## Install AWS CLI v2 (in the EC2)

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

## Aditional Packages

### Zip
```bash
  sudo apt-get upgrade
  sudo apt update
  sudo apt install -y zip unzip curl
  ```

### venv
To create python virtual environments you will need `venv` Check the version of python you have is compatible with venv.

```bash
sudo apt update
sudo apt install -y "python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')-venv"
```

If the previous does not work you can try:
  ```bash
  PY_MM=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
  sudo apt update
  sudo apt install -y "python${PY_MM}-venv" || sudo apt install -y python3-venv
  ```


## Verification

- Verify group membership before and after:
  ```bash
  # Before
  id -nG
  # Expected Output: ubuntu adm cdrom sudo dip lxd

  # Apply docker group membership
  sudo usermod -aG docker ubuntu
  newgrp docker

  # After
  id -nG
  # Expected Output: docker adm cdrom sudo dip lxd ubuntu

  # finally if the Docker daemon is not running:
  sudo systemctl start docker

  # Check
  docker ps
  ```

- Why this helps `docker ps`:
  Docker CLI talks to the Docker daemon through `/var/run/docker.sock`.
  That socket is commonly owned by `root:docker` with `srw-rw----`, so only `root` and users in the `docker` group can access it.
  After adding `ubuntu` to `docker` and reloading groups with `newgrp docker`, `docker ps` can connect without `sudo`.


## Important final steps

- Run this command to reboot the ec2 and reconnect to the instance. In this way the changes will be applied permanently (`sudo usermod -aG docker ubuntu`):

```bash
sudo reboot

# ... reconnect to the EC2 instance

# Check Service status (most direct)
sudo systemctl status docker

# if the Docker daemon is not running:
sudo systemctl start docker

# Finally check:
docker ps
```
