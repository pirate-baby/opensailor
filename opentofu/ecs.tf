resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.app_name}-ecs-task-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.app_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  container_definitions = jsonencode([
    {
      name         = "nginx"
      image        = "${aws_ecr_repository.nginx.repository_url}:latest"
      portMappings = [{ containerPort = 80 }]
    },
    {
      name         = "app"
      image        = "${aws_ecr_repository.app.repository_url}:latest"
      portMappings = [{ containerPort = 8000 }]

      environment = [
        { name = "DEBUG", value = "False" },
        { name = "APP_DB_USER", value = "opensailor" },
        { name = "APP_DB", value = "opensailor" },
        { name = "AWS_S3_STORAGE_BUCKET", value = "opensailor-public-storage" },
        { name = "AWS_DEFAULT_REGION_NAME", value = "us-east-2" },
        { name = "AWS_S3_ENDPOINT_URL", value = "https://s3.us-east-2.amazonaws.com" },
        { name = "AWS_S3_CLIENT_ENDPOINT_URL", value = "https://s3.us-east-2.amazonaws.com" },
        { name = "POSTGRES_HOST", value = aws_db_instance.main.endpoint },
        { name = "POSTGRES_PORT", value = "5432" },
      ]
      secrets = [
        { name = "DJANGO_SECRET_KEY", valueFrom = "${aws_secretsmanager_secret.env_vars.arn}:DJANGO_SECRET_KEY::" },
        { name = "APP_DB_PASSWORD", valueFrom = "${aws_secretsmanager_secret.env_vars.arn}:APP_DB_PASSWORD::" },
        { name = "GOOGLE_CLIENT_ID", valueFrom = "${aws_secretsmanager_secret.env_vars.arn}:GOOGLE_CLIENT_ID::" },
        { name = "GOOGLE_CLIENT_SECRET", valueFrom = "${aws_secretsmanager_secret.env_vars.arn}:GOOGLE_CLIENT_SECRET::" },
        { name = "GITHUB_CLIENT_ID", valueFrom = "${aws_secretsmanager_secret.env_vars.arn}:GITHUB_CLIENT_ID::" },
        { name = "GITHUB_CLIENT_SECRET", valueFrom = "${aws_secretsmanager_secret.env_vars.arn}:GITHUB_CLIENT_SECRET::" },
      ]
    }
  ])
}

resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.public[*].id
    assign_public_ip = true
    security_groups  = [aws_security_group.ecs.id]
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "nginx"
    container_port   = 80
  }
  depends_on = [aws_lb_listener.http]
}