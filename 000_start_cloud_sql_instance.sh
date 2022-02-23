#!/bin/bash
set -euo pipefail

readonly SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -o allexport; source  ${SCRIPT_DIR}/.env_cloud-wars-postgres; set +o allexport
cd $SCRIPT_DIR

#################################################################### DELETE INSTANCE
# gcloud sql instances delete ${CLOUD_SQL_INSTANCE_NAME}

#################################################################### CREATE INSTANCE
# gcloud sql instances create ${CLOUD_SQL_INSTANCE_NAME} \
# --database-version=POSTGRES_14 \
# --cpu=1 \
# --memory=3840MB \
# --zone=${REGION}-a \
# --storage-type=HDD \
# --storage-size=10 

#################################################################### SET DEFAULT USER PWD
# gcloud sql users set-password ${DB_USER} \
# --instance=${CLOUD_SQL_INSTANCE_NAME} \
# --password=${DB_PASS}

#################################################################### STOP INSTANCE
# gcloud sql instances patch ${CLOUD_SQL_INSTANCE_NAME} \
#   --project ${PROJECT_ID} \
#   --activation-policy=NEVER

#################################################################### START INSTANCE
# gcloud sql instances patch ${CLOUD_SQL_INSTANCE_NAME} \
#   --project ${PROJECT_ID} \
#   --activation-policy=ALWAYS

#################################################################### ENABLE HA
# gcloud sql instances patch ${CLOUD_SQL_INSTANCE_NAME} \
#   --project ${PROJECT_ID} \
#   --availability-type=REGIONAL

#################################################################### DISABLE HA
# gcloud sql instances patch ${CLOUD_SQL_INSTANCE_NAME} \
#   --project ${PROJECT_ID} \
#   --availability-type=ZONAL

################################################################### GET HA status
# gcloud sql instances describe ${CLOUD_SQL_INSTANCE_NAME} | grep availabilityType

#################################################################### INITIATE FAILOVER
# gcloud sql instances failover ${CLOUD_SQL_INSTANCE_NAME}
