####testing

import pytest
from datetime import datetime
from etl import extract_data, transform_data, load_data

@pytest.fixture
def setup_database(mocker):
    # Mock the database connection and cursor
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.side_effect = [
        (1, 1, 22.5, 60.1, datetime(2024, 9, 17, 17, 17, 43, 358526)),
        (2, 2, 23.0, 61.2, datetime(2024, 9, 17, 17, 17, 43, 358526)),
        None
    ]
    mock_conn = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect = mocker.patch('etl.psycopg2.connect', return_value=mock_conn)
    
    # Setup your database (e.g., create tables and insert initial data)
    conn = mock_connect()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS sensor_data (id SERIAL PRIMARY KEY, sensor_id INT, temperature_celsius FLOAT, humidity_percentage FLOAT, recorded_at TIMESTAMP)")
    cursor.execute("INSERT INTO sensor_data (sensor_id, temperature_celsius, humidity_percentage, recorded_at) VALUES (1, 22.5, 60.1, '2024-09-17 17:17:43')")
    cursor.execute("INSERT INTO sensor_data (sensor_id, temperature_celsius, humidity_percentage, recorded_at) VALUES (2, 23.0, 61.2, '2024-09-17 17:17:43')")
    conn.commit()

    yield

    # Teardown your database (e.g., drop tables)
    cursor.execute("DROP TABLE IF EXISTS sensor_data")
    conn.commit()
    cursor.close()
    conn.close()

def test_extract_data(setup_database):
    extracted_data = list(extract_data())
    assert len(extracted_data) == 2

def test_transform_data(setup_database):
    extracted_data = list(extract_data())
    transformed_data = transform_data(extracted_data)
    assert transformed_data[0] == {
        "id": 1,
        "sensor_id": 1,
        "temperature_celsius": 22.5,
        "humidity_percentage": 60.1,
        "recorded_at": "2024-09-17 17:17:43"
    }

def test_load_data(setup_database, mocker):
    # Extract the data first using the mock database
    extracted_data = list(extract_data())
    
    # Transform the extracted data
    transformed_data = transform_data(extracted_data)

    # Mock the MinIO client
    minio_client = mocker.MagicMock()
    mocker.patch('etl.Minio', return_value=minio_client)
    
    # Call load_data with the transformed data
    filename = load_data(transformed_data)

    # Assertions
    assert filename.endswith(".csv")  # Check if the filename has the correct extension
    minio_client.fput_object.assert_called_once_with(
        "data-lake-test",  # Replace with your bucket name
        filename,
        filename
    )
