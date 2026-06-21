# ═══════════════════════════════════════════════════════════════
# SentinelX — Terraform Provider Configuration
# This tells Terraform to use AWS as the cloud provider
# ═══════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS provider with our region
provider "aws" {
  region = var.aws_region
}
