resource "cloudflare_zone" "opensailor" {
  zone       = "opensailor.org"
  account_id = var.cloudflare_account_id
  plan       = "free"
  type       = "full"
}

resource "cloudflare_zone_settings_override" "opensailor_settings" {
  zone_id = cloudflare_zone.opensailor.id
  settings {
    ssl = "full"  # Use "full" mode for S3 compatibility (not "full_strict")
  }
}

resource "cloudflare_record" "root" {
  zone_id = cloudflare_zone.opensailor.id
  name    = "opensailor.org"
  content = aws_lb.app.dns_name
  type    = "CNAME"
  proxied = true
}

resource "cloudflare_record" "www" {
  zone_id = cloudflare_zone.opensailor.id
  name    = "www"
  content = aws_lb.app.dns_name
  type    = "CNAME"
  proxied = true
}

resource "cloudflare_record" "static" {
  zone_id = cloudflare_zone.opensailor.id
  name    = "static"
  content = "${aws_s3_bucket.static.id}.s3.${var.aws_region}.amazonaws.com"
  type    = "CNAME"
  proxied = true
}

resource "cloudflare_page_rule" "static_cache" {
  zone_id  = cloudflare_zone.opensailor.id
  target   = "static.opensailor.org/*"
  priority = 1

  actions {
    cache_level         = "cache_everything"
    edge_cache_ttl      = 2678400
    browser_cache_ttl   = 2678400
  }
}