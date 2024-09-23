import psycopg2
import csv
from datetime import datetime
from minio import Minio


def extract_data():
    conn = None
    cursor = None
    data = []
    try:
        conn = psycopg2.connect(
            database="sensor",
            user="root",
            password="Solorio78813",
            host="localhost",
            port="5432",
        )
        cursor = conn.cursor()
        # Execute a query
        cursor.execute("SELECT * FROM sensor_data")  # Replace with your actual query
        # Fetch rows lazily using yield
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            # Convert the datetime object to a string in the desired format
            row = list(row)  # Convert tuple to list to modify
            if isinstance(row[4], datetime):
                row[4] = row[4].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )  # Format the datetime if exists
            data.append(tuple(row))  # Convert back to tuple and yield it

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        # Close the cursor and connection when done
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return data


def transform_data(data):
    transformed = []
    for row in data:
        transformed.append(
            {
                "id": row[0],
                "sensor_id": row[1],
                "temperature_celsius": row[2],
                "humidity_percentage": row[3],
                "recorded_at": row[4].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(row[4], datetime)
                else row[4],
            }
        )
    return transformed


def load_data(transformed):
    filename = f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "id",
                "sensor_id",
                "temperature_celsius",
                "humidity_percentage",
                "recorded_at",
            ],
        )
        writer.writeheader()
        for row in transformed:
            writer.writerow(row)

    minio_client = Minio(
        "localhost:9000",
        access_key="UFTNrNMIDBiirdau",
        secret_key="MUDYl2cHQZWiGfgZkMRvAst5t0rldibc",
        secure=False,
    )

    minio_client.fput_object("data-lake-test", filename, filename)

    return filename


def verify_minio_data():
    from minio import Minio

    # Initialize MinIO client
    client = Minio(
        "localhost:9000",
        access_key="UFTNrNMIDBiirdau",
        secret_key="MUDYl2cHQZWiGfgZkMRvAst5t0rldibc",
        secure=False,
    )
    objects = client.list_objects("data-lake-test", recursive=True)
    for obj in objects:
        print(obj.object_name)


if __name__ == "__main__":
    data = extract_data()
    transformed = transform_data(data)
    load_data(transformed)
    verify_minio_data()
