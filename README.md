# Cloud Wars

Sample app to demonstrate:
1. (branch ```bq-insertall```): BQ streaming inserts to BigQuery with ```tabledata.insertAll``` method.
2. (branch ```bq-write-api```): BQ streaming inserts to BigQuery with Storage Write API.
3. (branch ```postgres```): inserts to Postgres on Cloud SQL.

Developed with Python version 3.9.

# How to run
Both local and Cloud Run setup requires you to:
1. Create a Postgres on Cloud SQL instance (e.g. with ```000_start_cloud_sql_instance.sh``` script).
2. Create ```.env_cloud-wars-postgres``` file based on ```.env_cloud-wars-postgres.example``` and replace environment variables with the correct values.
3. Authorize the gcloud CLI tools to use your user account credentials to access GCP ([gcloud CLI documentation](https://cloud.google.com/sdk/docs/initializing))

## 1. Running locally
1. Prepare environment (operating from projet's root direstory)
    * Create a virtual environment
    * Activate it
    * Update pip
    * Install requirements
    ```bash
    python -m venv .venv
    source .venv/Scripts/activate
    # Inside (.venv):
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```
    If any of above is unclear, get acustomed with the [python setup guide](https://cloud.google.com/python/setup).
3. Run the Cloud SQL Auth Proxy to connect to your Cloud SQL instance using TCP socket [Cloud SQL Proxy guide](https://cloud.google.com/sql/docs/mysql/connect-admin-proxy#start-proxy)
4. Run the app
    ```bash
    python main.py
    ```
5. Navigate towards `http://127.0.0.1:8081` to verify if your application is running correctly.

---
## 2. Running on Cloud Run
1. Build and deploy
    ```bash
    source 010_build_and_deploy.sh
    ```

2. Navigate your browser to the URL output at the end of the deployment process.

    **Your Cloud Run app will be accessible to everyone. Remember to delete it after use to avoid costs.**

    ##### For more details about using Cloud Run see the [Cloud Run documentation](https://cloud.google.com/sql/docs/postgres/connect-run)

---

## 3. Testing with Locust
1. (Inside locust directory):
    ```bash
    locust
    ```
2. Navigate towards `http://127.0.0.1:8089`.
3. Provide application url (either run locally or on Cloud Run) without the trailing slash - i.e. '/' and number of users.
4. Start the swarm.
