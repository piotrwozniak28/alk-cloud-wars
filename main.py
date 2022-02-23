import os
import logging
import datetime
from flask import Flask, render_template, request, Response
from google.cloud import bigquery

APP_ENV_INFO = os.getenv("APP_ENV_INFO")
DB_ENV_INFO = os.getenv("DB_ENV_INFO")
PROJECT_ID = os.getenv("PROJECT_ID")
BQD_STREAMING = os.getenv("BQD_STREAMING")
TABLE_NAME = os.getenv("TABLE_NAME")
BQ_TABLE_ID = f'{PROJECT_ID}.{BQD_STREAMING}.{TABLE_NAME}'

LOGGER = logging.getLogger()
BQ = bigquery.Client()
app = Flask(__name__)


@app.before_first_request
def create_tables():
    schema = [
        bigquery.SchemaField("time_cast", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("candidate", "STRING",
                             mode="REQUIRED", max_length=5),
    ]

    table = bigquery.Table(BQ_TABLE_ID, schema=schema)
    table = BQ.create_table(table, exists_ok=True)  # Make an API request.


@app.route('/', methods=['GET'])
def index():
    context = get_index_context()
    return render_template('index.html', **context)


def get_index_context():
    return {
        'front_db_info': DB_ENV_INFO,
        'front_app_info': APP_ENV_INFO
    }


@app.route('/', methods=['POST'])
def save_vote():
    cloud = request.form['cloud']
    time_cast = datetime.datetime.now(tz=datetime.timezone.utc)
    # Verify that the cloud is one of the allowed options
    if cloud != "AWS" and cloud != "Azure" and cloud != "GCP":
        LOGGER.warning(cloud)
        return Response(
            response="Invalid cloud specified.",
            status=400
        )

    try:
        table_insert_rows(time_cast=time_cast.isoformat(
        ), candidate=cloud, table_id=BQ_TABLE_ID)
    except Exception as e:
        print(e)

    return Response(
        status=200,
        response="Vote successfully cast for '{}' at time {}!".format(
            cloud, time_cast)
    )


def table_insert_rows(time_cast, candidate, table_id=BQ_TABLE_ID):

    rows_to_insert = [
        {"time_cast": time_cast, "candidate": candidate}
    ]

    # Using row_ids enables best effort de-duplication
    # https://cloud.google.com/bigquery/streaming-data-into-bigquery#dataconsistency
    # errors = BQ.insert_rows_json(table_id, rows_to_insert, row_ids='1') # Make an API request.
    errors = BQ.insert_rows_json(table_id, rows_to_insert) # Make an API request.
    if errors != []:
        LOGGER.exception(errors)
        raise
    LOGGER.info("Vote successfully cast for '{}' at time {}!".format(
        candidate, time_cast))


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env_cloud-wars-bq-insertall", verbose=True, override=True)
    os.environ["APP_ENV_INFO"] = "Run directly with main.py"
    app.run(host='127.0.0.1', port=8081, debug=True)
