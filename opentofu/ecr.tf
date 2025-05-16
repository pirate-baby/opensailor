resource "aws_ecr_repository" "app" {
  name = "${var.app_name}-app"
}

resource "aws_ecr_repository" "nginx" {
  name = "${var.app_name}-nginx"
}

resource "aws_ecr_repository" "db_startup" {
  name = "${var.app_name}-db-startup"
}