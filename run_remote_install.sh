#!/bin/bash
echo "Starting remote Docker installation on serveradrvesta1..."
echo "You will be prompted for the sudo password for user 'sorin' on the server."
ssh -t serveradrvesta1 "sudo bash -c 'apt update && apt install -y docker.io docker-compose-v2 && systemctl enable --now docker && usermod -aG docker sorin'"
echo "Installation complete. Please log out and back in for group changes to take effect."
