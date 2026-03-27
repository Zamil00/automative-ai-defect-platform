# Azure deployment outline

Recommended target:
- Frontend: Azure Static Web Apps
- Backend: Azure Container Apps or Azure App Service
- Database: Azure Database for PostgreSQL
- Storage: Azure Blob Storage for uploaded images and model artifacts

Suggested steps:
1. Push the backend container image to Azure Container Registry.
2. Provision Azure Database for PostgreSQL.
3. Configure environment variables and managed identity / secrets.
4. Deploy the backend container to Azure Container Apps.
5. Build the frontend with `VITE_API_BASE` set to the backend URL.
6. Deploy the frontend to Azure Static Web Apps.
7. Add CI/CD through GitHub Actions with separate staging and production environments.
