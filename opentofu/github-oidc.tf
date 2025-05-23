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
          "ecs:UpdateService"
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
          "ecr:CompleteLayerUpload"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::opensailor-tfstate",
          "arn:aws:s3:::opensailor-tfstate/*"
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
          "dynamodb:UpdateItem"
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

resource "aws_iam_role" "github_actions_drift" {
  name = "${var.app_name}-github-actions-drift"
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

resource "aws_iam_role_policy_attachment" "github_actions_drift_readonly" {
  role       = aws_iam_role.github_actions_drift.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

resource "aws_iam_policy" "github_actions_drift_tfstate_lock" {
  name        = "${var.app_name}-github-actions-drift-tfstate-lock"
  description = "Allow GitHub Actions drift role to access DynamoDB state lock table"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem"
        ],
        Resource = "arn:aws:dynamodb:us-east-2:*:table/opensailor-tfstate-lock"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_drift_tfstate_lock" {
  role       = aws_iam_role.github_actions_drift.name
  policy_arn = aws_iam_policy.github_actions_drift_tfstate_lock.arn
}

resource "aws_iam_policy" "github_actions_drift_secretsmanager" {
  name        = "${var.app_name}-github-actions-drift-secretsmanager"
  description = "Allow GitHub Actions drift role to read secrets for drift detection"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = [
          "arn:aws:secretsmanager:us-east-2:*:secret:opensailor*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_drift_secretsmanager" {
  role       = aws_iam_role.github_actions_drift.name
  policy_arn = aws_iam_policy.github_actions_drift_secretsmanager.arn
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions_deploy.arn
  description = "IAM Role ARN for GitHub Actions OIDC deploys. Use this in your GitHub Actions workflow as role-to-assume."
}

output "github_actions_drift_role_arn" {
  value = aws_iam_role.github_actions_drift.arn
  description = "IAM Role ARN for GitHub Actions OIDC drift detection. Use this in your GitHub Actions workflow as role-to-assume."
}