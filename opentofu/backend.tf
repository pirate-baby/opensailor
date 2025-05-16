terraform {
  backend "s3" {
    bucket         = "opensailor-tfstate"
    key            = "state/opensailor.tfstate"
    region         = "us-east-2"
    dynamodb_table = "opensailor-tfstate-lock"
    encrypt        = true
  }
}