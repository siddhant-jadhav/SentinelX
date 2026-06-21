# ═══════════════════════════════════════════════════════════════
# SentinelX — Main Terraform Configuration
# Creates a simple EC2 instance with a security group to run
# the SentinelX application using Docker
# ═══════════════════════════════════════════════════════════════

# ── Security Group ───────────────────────────────────────────────
# This acts as a firewall — controls what traffic can reach our server

resource "aws_security_group" "sentinelx_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH, HTTP, and app traffic for SentinelX"

  # Allow SSH access (port 22) — so we can connect to the server
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTP access (port 80)
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow Streamlit frontend (port 8503)
  ingress {
    description = "Streamlit Frontend"
    from_port   = var.frontend_port
    to_port     = var.frontend_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow FastAPI backend (port 8003)
  ingress {
    description = "FastAPI Backend"
    from_port   = var.backend_port
    to_port     = var.backend_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic — so server can download packages
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# ── EC2 Instance ─────────────────────────────────────────────────
# This is the virtual server that will run our application

resource "aws_instance" "sentinelx_server" {
  ami                    = "ami-0c7217cdde317cfec" # Ubuntu 22.04 LTS (us-east-1)
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.sentinelx_sg.id]

  # Script that runs when the server starts for the first time
  user_data = file("${path.module}/userdata.sh")

  tags = {
    Name = "${var.project_name}-server"
  }
}
