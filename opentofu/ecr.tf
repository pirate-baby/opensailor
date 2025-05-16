resource "aws_ecr_repository" "app" {
  name = "${var.app_name}-app"
}

resource "aws_ecr_repository" "nginx" {
  name = "${var.app_name}-nginx"
}