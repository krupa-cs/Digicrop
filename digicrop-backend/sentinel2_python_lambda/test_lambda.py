import unittest
from unittest.mock import patch, MagicMock
import json
import sys

# Force UTF-8 encoding for Windows console to support ✓ and ✗ characters
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import lambda_function

class CustomTestResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.test_records = []

    def startTest(self, test):
        super().startTest(test)
        desc = test.shortDescription() or test._testMethodName
        print(f"\n[RUNNING] {desc}...")

    def addSuccess(self, test):
        super().addSuccess(test)
        desc = test.shortDescription() or test._testMethodName
        print(f"  ✓ {desc} Passed")
        self.test_records.append({"status": "Passed", "desc": desc})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        desc = test.shortDescription() or test._testMethodName
        print(f"  ✗ {desc} Failed")
        print(f"    Reason: {err[1]}")
        self.test_records.append({"status": "Failed", "desc": desc, "error": str(err[1])})

    def addError(self, test, err):
        super().addError(test, err)
        desc = test.shortDescription() or test._testMethodName
        print(f"  ✗ {desc} Error")
        print(f"    Reason: {err[1]}")
        self.test_records.append({"status": "Failed", "desc": desc, "error": str(err[1])})

class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.s3_client')
    def test_post_success(self, mock_s3_client):
        """POST API Test"""
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "serialNumber": "S180H120L126-02",
                "dataType": "SENTINEL2",
                "result": {"band1": 0.5}
            })
        }
        
        response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['message'], "Data saved to S3")
        self.assertEqual(body['key'], "sentinel2/S180H120L126-02/S180H120L126-02.json")
        
        mock_s3_client.put_object.assert_called_once()

    @patch('lambda_function.s3_client')
    def test_post_missing_fields(self, mock_s3_client):
        """Missing Parameter Validation"""
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "serialNumber": "S180H120L126-02"
                # missing dataType and result
            })
        }
        
        response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])

    @patch('lambda_function.s3_client')
    def test_get_success(self, mock_s3_client):
        """GET API Test"""
        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "sentinel2/S180H120L126-02/S180H120L126-02.json"}]
        }
        
        mock_body = MagicMock()
        mock_body.read.return_value = json.dumps({"serialNumber": "S180H120L126-02", "dataType": "SENTINEL2", "result": {}}).encode('utf-8')
        mock_s3_client.get_object.return_value = {"Body": mock_body}
        
        event = {
            "httpMethod": "GET",
            "queryStringParameters": {
                "serialNumber": "S180H120L126-02",
                "dataType": "SENTINEL2"
            }
        }
        
        response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['count'], 1)
        self.assertEqual(len(body['data']), 1)

    @patch('lambda_function.s3_client')
    def test_get_not_found(self, mock_s3_client):
        """Error Handling"""
        mock_s3_client.list_objects_v2.return_value = {} # No Contents
        
        event = {
            "httpMethod": "GET",
            "queryStringParameters": {
                "serialNumber": "S180H120L126-02",
                "dataType": "SENTINEL2"
            }
        }
        
        response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertEqual(body['message'], "No data found")

if __name__ == '__main__':
    # Load all tests from the TestLambdaFunction class
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLambdaFunction)
    
    # Run tests using the custom test result to format output
    result = CustomTestResult()
    suite.run(result)
    
    # Print formatted summary
    print("\n========================================")
    print("Sentinel2 Lambda Test Summary")
    print("========================================")
    
    for record in result.test_records:
        if record["status"] == "Passed":
            print(f"✓ {record['desc']} Passed")
        else:
            print(f"✗ {record['desc']} Failed")
            
    total = len(result.test_records)
    passed = sum(1 for r in result.test_records if r["status"] == "Passed")
    failed = total - passed
    
    print(f"\nTotal Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}\n")
    
    if failed == 0:
        print("All tests completed successfully.")
    else:
        print("Some tests failed. Please review the output above.")
    print("========================================")
    
    # Exit with appropriate status code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)
