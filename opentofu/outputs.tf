output "alb_dns_name" {
  value = aws_lb.app.dns_name
}
output "s3_bucket" {
  value = aws_s3_bucket.static.bucket
}
output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}
output "ecr_repo_url" {
  value = aws_ecr_repository.app.repository_url
}

output "cloudflare_zone_id" {
  value = cloudflare_zone.opensailor.id
}

output "cloudflare_nameservers" {
  value = cloudflare_zone.opensailor.name_servers
}