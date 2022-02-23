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
  --set-env-vars PROJECT_ID=${PROJECT_ID},BQD_STREAMING=${BQD_STREAMING},TABLE_NAME=${TABLE_NAME},APP_ENV_INFO="${APP_ENV_INFO}",DB_ENV_INFO="${DB_ENV_INFO}" \
  --project ${PROJECT_ID} \
  --allow-unauthenticated
  