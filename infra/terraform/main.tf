terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to store state in S3 (recommended for team use)
  # backend "s3" {
  #   bucket = "ananas-ai-terraform-state"
  #   key    = "production/terraform.tfstate"
  #   region = "eu-central-1"
  # }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "ananas-ai"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# ── Data ──────────────────────────────────────────────────────────────────────

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# ── VPC (minimal — single AZ, no NAT gateway needed for outbound-only agents) ─

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "ananas-ai-vpc" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = { Name = "ananas-ai-public" }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "ananas-ai-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "ananas-ai-rt-public" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ── Security Group ────────────────────────────────────────────────────────────

resource "aws_security_group" "runtime" {
  name        = "ananas-ai-runtime"
  description = "Ananas AI runtime host — SSH from trusted IPs, all outbound"
  vpc_id      = aws_vpc.main.id

  dynamic "ingress" {
    for_each = length(var.allowed_ssh_cidrs) > 0 ? [1] : []
    content {
      description = "SSH from trusted IPs"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = var.allowed_ssh_cidrs
    }
  }

  # Outbound: agents call external APIs, Teams, email, etc.
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound — agents call external APIs"
  }

  tags = { Name = "ananas-ai-runtime-sg" }
}

# ── IAM Role for EC2 ──────────────────────────────────────────────────────────

resource "aws_iam_role" "runtime" {
  name = "ananas-ai-runtime-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "runtime" {
  name = "ananas-ai-runtime-policy"
  role = aws_iam_role.runtime.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "SecretsManager"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:ananas-ai/*"
      },
      {
        Sid    = "S3Backups"
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket", "s3:DeleteObject"]
        Resource = [
          aws_s3_bucket.backups.arn,
          "${aws_s3_bucket.backups.arn}/*",
        ]
      },
      {
        Sid    = "CloudWatchLogs"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "cloudwatch:PutMetricData",
        ]
        Resource = "*"
      },
      {
        Sid    = "SSMParameters"
        Effect = "Allow"
        Action = ["ssm:GetParameter", "ssm:GetParameters"]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/ananas-ai/*"
      },
    ]
  })
}

resource "aws_iam_instance_profile" "runtime" {
  name = "ananas-ai-runtime-profile"
  role = aws_iam_role.runtime.name
}

# ── EC2 Instance ──────────────────────────────────────────────────────────────

resource "aws_instance" "runtime" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.runtime.id]
  iam_instance_profile   = aws_iam_instance_profile.runtime.name
  key_name               = var.key_pair_name

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.ebs_volume_size_gb
    encrypted             = true
    delete_on_termination = false  # keep data on instance replace

    tags = { Name = "ananas-ai-root-vol" }
  }

  user_data = base64encode(templatefile("${path.module}/../scripts/bootstrap_ec2.sh", {
    github_repo = var.github_repo
    db_name     = var.db_name
    db_user     = var.db_user
    aws_region  = var.aws_region
  }))

  tags = { Name = "ananas-ai-runtime" }

  lifecycle {
    ignore_changes = [ami]  # don't replace instance on AMI updates
  }
}

# ── Elastic IP ────────────────────────────────────────────────────────────────

resource "aws_eip" "runtime" {
  instance = aws_instance.runtime.id
  domain   = "vpc"
  tags     = { Name = "ananas-ai-eip" }
}
