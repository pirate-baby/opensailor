resource "aws_db_instance" "main" {
  identifier              = "${var.app_name}-pg"
  engine                  = "postgres"
  engine_version          = "15"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  username                = var.db_username
  password                = random_password.db_password.result
  db_name                 = "appdb"
  vpc_security_group_ids  = [aws_security_group.rds.id]
  db_subnet_group_name    = aws_db_subnet_group.pg.name
  skip_final_snapshot     = true
  publicly_accessible     = false
  backup_retention_period = 1
}

resource "aws_db_subnet_group" "pg" {
  name       = "${var.app_name}-pg-subnet"
  subnet_ids = aws_subnet.public[*].id
}