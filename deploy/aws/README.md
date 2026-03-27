# AWS deployment outline

Recommended target:
- Frontend: S3 + CloudFront
- Backend: ECS Fargate or App Runner
- Database: Amazon RDS for PostgreSQL
- Artifacts: S3 for uploaded images and model versions

Suggested steps:
1. Build and push backend image to Amazon ECR.
2. Provision PostgreSQL in RDS.
3. Set environment variables such as `DATABASE_URL`, `CORS_ORIGINS`, and `MODEL_PATH`.
4. Deploy backend to ECS Fargate or App Runner.
5. Build frontend with `VITE_API_BASE` pointing to the public backend URL.
6. Upload frontend build to S3 and serve through CloudFront.
7. Add GitHub Actions for CI/CD and environment-specific secrets.
