variable "aws_region" {
  description = "AWS region — eu-central-1 (Frankfurt) is closest to MKD"
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance type for the runtime host"
  type        = string
  default     = "t3.small"   # 2 vCPU / 2GB — cheapest viable; scale up when needed
}

variable "ebs_volume_size_gb" {
  description = "EBS root volume size in GB"
  type        = number
  default     = 20
}

variable "allowed_ssh_cidrs" {
  description = "CIDR blocks allowed to SSH into the instance — restrict to your IP"
  type        = list(string)
  default     = []  # MUST be set — empty = no SSH access
}

variable "domain_name" {
  description = "Domain for the AI portal"
  type        = string
  default     = "ai.ananas.mk"
}

variable "alert_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = ""
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "ananas_ai"
}

variable "db_user" {
  description = "PostgreSQL database user"
  type        = string
  default     = "ananas_ai"
}

variable "s3_backup_retention_days" {
  description = "Days to retain nightly DB backups in S3"
  type        = number
  default     = 30
}

variable "key_pair_name" {
  description = "EC2 Key Pair name for SSH access (must already exist in AWS)"
  type        = string
  default     = "ananas-ai-key"
}

variable "github_repo" {
  description = "GitHub repo to clone on bootstrap (owner/repo format)"
  type        = string
  default     = "zhapostolski/ananas-ai"
}
