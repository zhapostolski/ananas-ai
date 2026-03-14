output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.runtime.id
}

output "public_ip" {
  description = "Elastic IP — use this in DNS and for SSH"
  value       = aws_eip.runtime.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_eip.runtime.public_ip}"
}

output "s3_backup_bucket" {
  description = "S3 bucket name for database backups"
  value       = aws_s3_bucket.backups.bucket
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

output "secrets_arns" {
  description = "ARNs of all Secrets Manager secrets — fill these in the AWS Console"
  value = {
    anthropic  = aws_secretsmanager_secret.anthropic.arn
    openai     = aws_secretsmanager_secret.openai.arn
    google     = aws_secretsmanager_secret.google.arn
    meta       = aws_secretsmanager_secret.meta.arn
    pinterest  = aws_secretsmanager_secret.pinterest.arn
    microsoft  = aws_secretsmanager_secret.microsoft.arn
    database   = aws_secretsmanager_secret.database.arn
  }
}
