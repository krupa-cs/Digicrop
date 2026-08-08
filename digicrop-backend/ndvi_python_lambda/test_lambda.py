import unittest
from unittest.mock import patch, MagicMock
import json
import sys

# Force UTF-8 encoding for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import lambda_function

class TestNDVILambda(unittest.TestCase):
    
    @patch('lambda_function.table')
    def test_missing_params(self, mock_table):
        event = {
            "queryStringParameters": {
                "PK": "ORG-123"
                # Missing PlotId
            }
        }
        response = lambda_function.handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], "PK and PlotId are required")

    @patch('lambda_function.table')
    def test_not_found(self, mock_table):
        mock_table.query.return_value = {"Items": []}
        event = {
            "queryStringParameters": {
                "PK": "ORG-123",
                "PlotId": "P-456"
            }
        }
        response = lambda_function.handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], "No NDVI data found for this plot")

    @patch('lambda_function.table')
    def test_success_payload_generation(self, mock_table):
        from decimal import Decimal
        mock_item = {
            "PK": "ORG-123",
            "SK": "PD-P-456#2024",
            "SerialNumber": "DEV-01",
            "Date": "2024-01-01",
            "CropType": "Wheat",
            "polygonAverageNDVI": Decimal('0.75'),
            "weather": {
                "temperature": Decimal('22'),
                "raw": {
                    "forecastDays": [
                        {
                            "sunEvents": {"sunriseTime": "06:00", "sunsetTime": "18:00"},
                            "maxTemperature": {"degrees": Decimal('28')},
                            "daytimeForecast": {"wind": {"speed": {"value": Decimal('10')}, "direction": {"cardinal": "N"}}}
                        }
                    ]
                }
            }
        }
        mock_table.query.return_value = {"Items": [mock_item]}
        
        event = {
            "queryStringParameters": {
                "PK": "ORG-123",
                "PlotId": "P-456"
            }
        }
        response = lambda_function.handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        payload = body['payload']
        
        # Verify payload mapping
        self.assertEqual(payload['PK'], "ORG-123")
        self.assertEqual(payload['NDVI'], 0.75)
        self.assertEqual(payload['weather']['temperature'], 22)
        self.assertEqual(payload['weather']['sunrise'], "06:00")
        self.assertEqual(payload['weather']['maxTemperature'], 28)
        self.assertEqual(payload['weather']['windSpeed'], 10)
        self.assertEqual(payload['weather']['windDirection'], "N")

if __name__ == '__main__':
    unittest.main(verbosity=2)
