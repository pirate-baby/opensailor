resource "aws_acm_certificate" "alb_cert" {
  domain_name               = "opensailor.org"
  subject_alternative_names = ["www.opensailor.org"]
  validation_method         = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}

output "acm_certificate_domain_validation_options" {
  value = aws_acm_certificate.alb_cert.domain_validation_options
  description = "ACM DNS validation records. Add these as CNAMEs in Namecheap."
}