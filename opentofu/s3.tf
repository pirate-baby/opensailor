resource "aws_s3_bucket" "static" {
  bucket        = "${var.app_name}-public-storage"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "static_acl" {
  bucket = aws_s3_bucket.static.id
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "static" {
  bucket                  = aws_s3_bucket.static.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.static.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject"]
      Resource  = "${aws_s3_bucket.static.arn}/*"
      Condition = {
        IpAddress = {
          "aws:SourceIp" = [
            "173.245.48.0/20",
            "103.21.244.0/22",
            "103.22.200.0/22",
            "103.31.4.0/22",
            "141.101.64.0/18",
            "108.162.192.0/18",
            "190.93.240.0/20",
            "188.114.96.0/20",
            "197.234.240.0/22",
            "198.41.128.0/17",
            "162.158.0.0/15",
            "104.16.0.0/13",
            "104.24.0.0/14",
            "172.64.0.0/13",
            "131.0.72.0/22"
          ]
        }
      }
    }]
  })
}

resource "aws_s3_bucket_versioning" "static" {
  bucket = aws_s3_bucket.static.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_cors_configuration" "static" {
  bucket = aws_s3_bucket.static.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["https://opensailor.org", "https://www.opensailor.org", "https://static.opensailor.org"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}