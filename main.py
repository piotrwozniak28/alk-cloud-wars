import os
import time
import logging
import datetime
from flask import Flask, render_template, request, Response
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1
from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1 import writer
from google.protobuf import descriptor_pb2
import proto_files.out.vote_pb2 as vote_pb2

APP_ENV_INFO = os.getenv("APP_ENV_INFO")
DB_ENV_INFO = os.getenv("DB_ENV_INFO")
PROJECT_ID = os.getenv("PROJECT_ID")
BQD_STREAMING = os.getenv("BQD_STREAMING")
TABLE_NAME = os.getenv("TABLE_NAME")

LOGGER = logging.getLogger()
BQ = bigquery.Client()
BQ_WRITE_CLIENT = bigquery_storage_v1.BigQueryWriteClient()
app = Flask(__name__)


def get_unixtime():
    # Microseconds since the Unix epoch for BQ TIMESTAMP type
    # https://cloud.google.com/bigquery/docs/write-api#default-stream
    return int(time.time()) * 1000 * 1000


@app.before_first_request
def create_dataset():
    dataset = bigquery.Dataset(f'{PROJECT_ID}.{BQD_STREAMING}')
    dataset.location = os.getenv("REGION")
    # Make an API request.
    BQ.create_dataset(dataset, exists_ok=True, timeout=15)


@app.before_first_request
def create_table():
    schema = [
        bigquery.SchemaField("time_cast", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("candidate", "STRING",
                             mode="REQUIRED", max_length=5),
    ]

    table = bigquery.Table(
        f'{PROJECT_ID}.{BQD_STREAMING}.{TABLE_NAME}', schema=schema)
    BQ.create_table(table, exists_ok=True, timeout=3)  # Make an API request.


@app.before_first_request
def create_append_rows_stream():
    global append_rows_stream
    write_stream = create_write_stream(PROJECT_ID, BQD_STREAMING, TABLE_NAME)
    request_template = create_request_template(write_stream)
    # Some stream types support an unbounded number of requests. Construct an
    # AppendRowsStream to send an arbitrary number of requests to a stream.
    append_rows_stream = writer.AppendRowsStream(
        BQ_WRITE_CLIENT, request_template)


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
        table_insert_rows(time_cast=get_unixtime(), candidate=cloud)
    except Exception as e:
        print(e)

    return Response(
        status=200,
        response="Vote successfully cast for '{}' at time {}!".format(
            cloud, time_cast)
    )


def table_insert_rows(time_cast, candidate):
    serialized_row_data = create_serialized_row_data(time_cast, candidate)
    proto_data = create_proto_data(serialized_row_data)
    request = create_request(proto_data)
    future = append_rows_stream.send(request)
    # print(future.result())


def create_write_stream(project_id, dataset_id, table_id):
    parent = BQ_WRITE_CLIENT.table_path(project_id, dataset_id, table_id)
    write_stream = types.WriteStream()
    write_stream.type_ = types.WriteStream.Type.COMMITTED
    write_stream = BQ_WRITE_CLIENT.create_write_stream(
        parent=parent, write_stream=write_stream
    )
    print(f"Write stream name: '{write_stream.name}' has been created.")
    return write_stream


def create_request_template(write_stream):
    request_template = types.AppendRowsRequest()
    # The initial request must contain the stream name.
    request_template.write_stream = write_stream.name
    # So that BigQuery knows how to parse the serialized_rows, generate a
    # protocol buffer representation of your message descriptor.
    proto_schema = types.ProtoSchema()
    proto_descriptor = descriptor_pb2.DescriptorProto()
    vote_pb2.Vote.DESCRIPTOR.CopyToProto(proto_descriptor)
    proto_schema.proto_descriptor = proto_descriptor
    proto_data = types.AppendRowsRequest.ProtoData()
    proto_data.writer_schema = proto_schema
    request_template.proto_rows = proto_data
    return request_template


def create_serialized_row_data(time_cast: str, candidate: str):
    row = vote_pb2.Vote()
    row.time_cast = time_cast
    row.candidate = candidate
    return row.SerializeToString()


def create_proto_data(serialized_row_data):
    # Create a batch of row data by appending proto2 serialized bytes to the
    # serialized_rows repeated field.
    proto_rows = types.ProtoRows()
    proto_rows.serialized_rows.append(serialized_row_data)
    proto_data = types.AppendRowsRequest.ProtoData()
    proto_data.rows = proto_rows
    return proto_data


def create_request(proto_data, offset=False):
    # Set an offset to allow resuming this stream if the connection breaks.
    # Keep track of which requests the server has acknowledged and resume the
    # stream at the first non-acknowledged message. If the server has already
    # processed a message with that offset, it will return an ALREADY_EXISTS
    # error, which can be safely ignored.
    #
    # The first request must always have an offset of 0.
    request = types.AppendRowsRequest()
    if offset:
        request.offset = offset
    request.proto_rows = proto_data
    return request


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env_cloud-wars-bq-write-api", verbose=True, override=True)
    os.environ["APP_ENV_INFO"] = "Run directly with main.py"
    app.run(host='127.0.0.1', port=8081, debug=True)
