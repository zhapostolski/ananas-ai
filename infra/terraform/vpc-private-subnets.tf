# Private subnets + NAT gateway for ananas-ai VPC
# Standalone improvement - protects current workload and prepares for ananas-hub
# Apply independently: terraform plan/apply from infra/terraform/
#
# What this adds:
#   - 2 private subnets (eu-central-1a + eu-central-1b) for ECS Fargate and RDS
#   - EIP + NAT gateway (in existing public subnet) for outbound internet from private subnets
#   - Private route table
#
# The existing EC2 instance and public subnet are NOT modified.
# Cost addition: ~$35/month (NAT gateway: $0.045/hr + $0.045/GB data)

# Pull in existing internet gateway from main.tf (already defined as aws_internet_gateway.main)

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]  # eu-central-1a

  tags = { Name = "ananas-ai-private-a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]  # eu-central-1b

  tags = { Name = "ananas-ai-private-b" }
}

resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = { Name = "ananas-ai-nat-eip" }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id  # NAT lives in the public subnet

  tags       = { Name = "ananas-ai-nat" }
  depends_on = [aws_internet_gateway.main]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = { Name = "ananas-ai-rt-private" }
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}
