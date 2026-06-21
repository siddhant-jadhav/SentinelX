#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# SentinelX — EC2 Startup Script
# This script runs automatically when the EC2 instance starts.
# It installs Docker, clones the project, and starts the app.
# ═══════════════════════════════════════════════════════════════

# Update the system packages
sudo apt-get update -y

# Install Docker
sudo apt-get install -y docker.io docker-compose-v2

# Start Docker and enable it on boot
sudo systemctl start docker
sudo systemctl enable docker

# Install Git
sudo apt-get install -y git

# Clone the SentinelX project
cd /home/ubuntu
git clone https://github.com/siddhant-jadhav/SentinelX.git
cd SentinelX

# Start the application using Docker Compose
sudo docker compose up -d --build

echo "SentinelX setup complete!"
