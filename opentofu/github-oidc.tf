# GitHub OIDC Provider
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"] # GitHub's root CA thumbprint
}

resource "aws_iam_role" "github_actions_deploy" {
  name = "${var.app_name}-github-actions-deploy"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      },
      Action = "sts:AssumeRoleWithWebIdentity",
      Condition = {
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:${var.github_repo}:*"
        }
      }
    }]
  })
}

# Policy for ECS and ECR deploy permissions
resource "aws_iam_policy" "github_actions_ecs_ecr" {
  name        = "${var.app_name}-github-actions-ecs-ecr"
  description = "Allow GitHub Actions to deploy to ECS and push/pull ECR images"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:DescribeTasks",
          "ecs:ListClusters",
          "ecs:ListServices",
          "ecs:ListTaskDefinitions",
          "ecs:ListTasks",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeClusters",
          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeInternetGateways",
          "ec2:DescribeRouteTables",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeVpcAttribute",
          "ec2:DescribeVpcEndpoints",
          "acm:DescribeCertificate",
          "acm:ListTagsForCertificate",
          "logs:DescribeLogGroups",
          "logs:ListTagsForResource",
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeTargetGroups",
          "rds:DescribeDBSubnetGroups"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:DescribeRepositoryPolicy",
          "ecr:GetRepositoryPolicy",
          "ecr:ListTagsForResource"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "iam:GetRole",
          "iam:GetOpenIDConnectProvider",
          "iam:GetPolicy",
          "iam:ListRolePolicies",
          "iam:GetPolicyVersion",
          "iam:ListAttachedRolePolicies",
          "iam:GetRolePolicy"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetResourcePolicy"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketPolicy",
          "s3:GetBucketAcl",
          "s3:GetBucketCORS",
          "s3:GetBucketWebsite"
        ],
        Resource = [
          "arn:aws:s3:::opensailor-tfstate",
          "arn:aws:s3:::opensailor-tfstate/*",
          "arn:aws:s3:::opensailor-public-storage",
          "arn:aws:s3:::opensailor-public-storage/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem",
          "dynamodb:DescribeTable",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:DescribeTimeToLive"
        ],
        Resource = "arn:aws:dynamodb:us-east-2:*:table/opensailor-tfstate-lock"
      },
      {
        Effect = "Allow",
        Action = [
          "iam:PassRole"
        ],
        Resource = [
          "arn:aws:iam::227647310737:role/opensailor-ecs-task-execution",
          "arn:aws:iam::227647310737:role/opensailor-ecs-task"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_ecs_ecr" {
  role       = aws_iam_role.github_actions_deploy.name
  policy_arn = aws_iam_policy.github_actions_ecs_ecr.arn
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions_deploy.arn
  description = "IAM Role ARN for GitHub Actions OIDC deploys. Use this in your GitHub Actions workflow as role-to-assume."
}