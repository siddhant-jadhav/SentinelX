# ═══════════════════════════════════════════════════════════════
# SentinelX — Terraform Outputs
# These values are displayed after running 'terraform apply'
# ═══════════════════════════════════════════════════════════════

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.sentinelx_server.id
}

output "public_ip" {
  description = "Public IP address of the server"
  value       = aws_instance.sentinelx_server.public_ip
}

output "frontend_url" {
  description = "URL to access SentinelX Frontend"
  value       = "http://${aws_instance.sentinelx_server.public_ip}:${var.frontend_port}"
}

output "backend_url" {
  description = "URL to access SentinelX API"
  value       = "http://${aws_instance.sentinelx_server.public_ip}:${var.backend_port}"
}

output "ssh_command" {
  description = "Command to SSH into the server"
  value       = "ssh -i ${var.key_pair_name}.pem ubuntu@${aws_instance.sentinelx_server.public_ip}"
}
