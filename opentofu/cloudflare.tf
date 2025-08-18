resource "cloudflare_zone" "opensailor" {
  zone       = "opensailor.org"
  account_id = var.cloudflare_account_id
  plan       = "free"
  type       = "full"
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

resource "cloudflare_page_rule" "static_cache" {
  zone_id  = cloudflare_zone.opensailor.id
  target   = "opensailor.org/static/*"
  priority = 1
  status   = "active"

  actions {
    cache_level         = "cache_everything"
    edge_cache_ttl      = 2678400
    browser_cache_ttl   = "2678400"
  }
}