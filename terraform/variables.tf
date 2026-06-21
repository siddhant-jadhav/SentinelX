# ═══════════════════════════════════════════════════════════════
# SentinelX — Terraform Variables
# All the configurable values for our infrastructure
# ═══════════════════════════════════════════════════════════════

# AWS region where resources will be created
variable "aws_region" {
  description = "AWS region to deploy in"
  type        = string
  default     = "us-east-1"
}

# Project name used for tagging resources
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "sentinelx"
}

# EC2 instance size (t2.micro is free tier eligible)
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

# SSH key pair name (must already exist in AWS)
variable "key_pair_name" {
  description = "Name of existing EC2 key pair for SSH access"
  type        = string
  default     = "sentinelx-key"
}

# Application ports
variable "backend_port" {
  description = "FastAPI backend port"
  type        = number
  default     = 8003
}

variable "frontend_port" {
  description = "Streamlit frontend port"
  type        = number
  default     = 8503
}
