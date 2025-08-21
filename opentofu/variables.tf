variable "aws_region" { default = "us-east-2" }
variable "app_name" { default = "opensailor" }
variable "env_secrets_name" { default = "opensailor" }
variable "github_repo" { default = "pirate-baby/opensailor" }

variable "cloudflare_api_key" {
  description = "Cloudflare API key"
  type        = string
  sensitive   = true
}
variable "cloudflare_email" {
  description = "Cloudflare account email"
  type        = string
  sensitive   = true
  default     = "ethan@knox.dev"
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
  sensitive   = true
}