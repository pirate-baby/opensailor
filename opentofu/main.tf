provider "aws" {
  region = var.aws_region
}

resource "aws_secretsmanager_secret" "env_vars" {
  name = var.env_secrets_name
}

resource "random_password" "db_password" {
  length          = 24
  special         = true
  override_special = "!#$%&()*+,-.:;<=>?[]^_{|}~"
}

resource "random_password" "django_secret_key" {
  length  = 50
  special = true
}
resource "aws_secretsmanager_secret_version" "env_vars" {
  secret_id = aws_secretsmanager_secret.env_vars.id
  secret_string = jsonencode({
    DEBUG                = 1
    DJANGO_SECRET_KEY    = random_password.django_secret_key.result
    APP_DB_PASSWORD      = random_password.db_password.result
    GOOGLE_CLIENT_ID     = "replace-me"
    GOOGLE_CLIENT_SECRET = "replace-me"
    GITHUB_CLIENT_ID     = "replace-me"
    GITHUB_CLIENT_SECRET = "replace-me"
  })
}

# Policy for app container to access S3 and RDS
resource "aws_iam_policy" "app_s3_rds" {
  name        = "${var.app_name}-app-s3-rds"
  description = "Allow app to read/write S3 and connect to RDS"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          "${aws_s3_bucket.static.arn}",
          "${aws_s3_bucket.static.arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "rds-db:connect"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "app_s3_rds" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.app_s3_rds.arn
}

# Policy for ECS to read secrets, create log groups, and write logs
resource "aws_iam_policy" "ecs_secrets_logs" {
  name        = "${var.app_name}-ecs-secrets-logs"
  description = "Allow ECS to read secrets, create log groups, and write logs"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = [aws_secretsmanager_secret.env_vars.arn]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_logs" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_secrets_logs.arn
}