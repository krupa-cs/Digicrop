import json
import boto3
import datetime
import decimal

# Custom JSON encoder to handle Decimal types returned by DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if obj % 1 > 0:
                return float(obj)
            else:
                return int(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MainTransactionData')

def lambda_handler(event, context):
    try:
        print(f"EVENT: {json.dumps(event)}")
        
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
            
        user_id = body.get('userId')
        plot_id = body.get('plotId')
        soil_ph = body.get('soil_ph')
        e_c = body.get('e_c')
        organic_carbon = body.get('organic_carbon')
        soil_test = body.get('soil_test')
        
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
        
        response = table.update_item(
            Key={
                'PK': user_id,
                'SK': f"PD-{plot_id}"
            },
            UpdateExpression="SET #ph = :ph, #ec = :ec, #oc = :oc, #st = :st, updatedAt = :ts",
            ExpressionAttributeNames={
                "#ph": "soil_ph",
                "#ec": "e_c",
                "#oc": "organic_carbon",
                "#st": "soil_test"
            },
            ExpressionAttributeValues={
                ":ph": soil_ph,
                ":ec": e_c,
                ":oc": organic_carbon,
                ":st": soil_test,
                ":ts": timestamp
            },
            ReturnValues="ALL_NEW"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'data': response.get('Attributes', {})
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
