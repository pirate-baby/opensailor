variable "aws_region" { default = "us-east-2" }
variable "app_name" { default = "opensailor" }
variable "env_secrets_name" { default = "opensailor" }
variable "github_repo" { default = "pirate-baby/opensailor" }

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
  sensitive   = true
}