from lambda_function import lambda_handler
import json

def test_missing_serial():
    print("Testing Missing SerialNumber...")
    event = {"queryStringParameters": {}}
    res = lambda_handler(event, None)
    print(json.dumps(res, indent=2))

def test_latest_record(serial_number):
    print(f"\nTesting Latest Record for {serial_number}...")
    event = {"queryStringParameters": {"SerialNumber": serial_number}}
    res = lambda_handler(event, None)
    print(json.dumps(res, indent=2))

def test_date_range(serial_number, start_date, end_date):
    print(f"\nTesting Date Range for {serial_number}...")
    event = {
        "queryStringParameters": {
            "SerialNumber": serial_number,
            "startDate": start_date,
            "endDate": end_date
        }
    }
    res = lambda_handler(event, None)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    # Replace 'TEST_DEVICE' with a real serial number in your database
    TEST_DEVICE_SERIAL = "TEST_DEVICE"
    
    test_missing_serial()
    test_latest_record(TEST_DEVICE_SERIAL)
    test_date_range(TEST_DEVICE_SERIAL, "2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z")
