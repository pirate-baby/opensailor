# OpenSailor.org

Sailing is about freedom. Sailing data should be to.

## Infrastructure as Code (OpenTofu)

Infrastructure for AWS ECS, ECR, Aurora, ALB, and S3 is managed in the `opentofu/` directory using OpenTofu (Terraform fork). See the files in `opentofu/` for details.

## Deployment

Deployment to AWS ECS is automated via GitHub Actions. See `.github/workflows/deploy.yml` for the deployment pipeline.