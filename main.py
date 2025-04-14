provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "eks_cluster" {
  name     = "my-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = aws_subnet.subnet_ids[*].id
  }
}

resource "aws_iam_role" "eks_cluster_role" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_subnet" "subnet" {
  count = 2
  cidr_block = cidrsubnet("10.0.0.0/16", 8, count.index)
  availability_zone = element(data.aws_availability_zones.available.names, count.index)
}

resource "aws_security_group" "eks_security_group" {
  name_prefix = "eks_sg"
  description = "Allow all inbound traffic"
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Outputs
output "cluster_endpoint" {
  value = aws_eks_cluster.eks_cluster.endpoint
}
output "cluster_name" {
  value = aws_eks_cluster.eks_cluster.name
}
