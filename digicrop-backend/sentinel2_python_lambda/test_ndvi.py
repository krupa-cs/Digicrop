import json
from lambda_function import lambda_handler

def test_ndvi():
    print("========================================")
    print("Testing NDVI Lambda Handler Locally")
    print("========================================\n")

    test_serial = "DEVICE_NDVI_123"
    test_data_type = "NDVI"
    test_result = {
        "mean_ndvi": 0.65,
        "max_ndvi": 0.82,
        "cloud_cover": 5.2
    }

    # 1. Test saving data (POST)
    print(f"[1] Testing POST Data for {test_serial} ({test_data_type})...")
    post_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "serialNumber": test_serial,
            "dataType": test_data_type,
            "result": test_result
        })
    }
    
    post_res = lambda_handler(post_event, None)
    print("Response Status Code:", post_res['statusCode'])
    print("Response Body:\n", json.dumps(json.loads(post_res['body']), indent=2))
    print("-" * 40)

    # 2. Test fetching data (GET)
    print(f"\n[2] Testing GET Data for {test_serial} ({test_data_type})...")
    get_event = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "serialNumber": test_serial,
            "dataType": test_data_type
        }
    }
    
    get_res = lambda_handler(get_event, None)
    print("Response Status Code:", get_res['statusCode'])
    print("Response Body:\n", json.dumps(json.loads(get_res['body']), indent=2))
    print("-" * 40)

if __name__ == "__main__":
    test_ndvi()
