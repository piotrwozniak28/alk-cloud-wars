#!/bin/bash
set -euo pipefail

readonly SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -o allexport; source  ${SCRIPT_DIR}/.env_cloud-wars-postgres; set +o allexport
cd $SCRIPT_DIR

gcloud builds submit \
  --tag gcr.io/${PROJECT_ID}/${APP_NAME} \
  --project ${PROJECT_ID}

gcloud run deploy ${APP_NAME} \
  --image gcr.io/${PROJECT_ID}/${APP_NAME} \
  --platform managed \
  --region ${REGION} \
  --add-cloudsql-instances "${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE_NAME}" \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE_NAME}",DB_USER=${DB_USER},DB_PASS=${DB_PASS},DB_NAME=${DB_NAME},APP_ENV_INFO="${APP_ENV_INFO}",DB_ENV_INFO="${DB_ENV_INFO}" \
  --project ${PROJECT_ID} \
  --allow-unauthenticated
