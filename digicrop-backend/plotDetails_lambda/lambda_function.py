import json
import uuid
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = "MainTransactionData"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))
    
    user_id = event.get('userId')
    date = event.get('date')
    name = event.get('name')
    latitude = event.get('latitude')
    longitude = event.get('longitude')
    crop_type = event.get('cropType')
    variety = event.get('variety')
    serial_number = event.get('serialNumber')
    soil_type = event.get('soilType')
    plot_location = event.get('plotLocation')
    polygon_points = event.get('polygonPoints', [])
    root_depth = event.get('root_depth')
    irrigation_efficiency = event.get('Irrigation_efficiency')
    target_yield_t_acre = event.get('target_yield_t_acre')
    fertilizer_application_method = event.get('fertilizer_application_method')
    area_of_field_acre = event.get('area_of_field_acre')
    age_years = event.get('age_years')
    plant_density_per_acre = event.get('plant_density_per_acre')

    # ---------- BASIC VALIDATION ----------
    if (
        not user_id or
        not date or
        not name or
        latitude is None or
        longitude is None or
        not crop_type or
        not serial_number or
        not soil_type or
        not plot_location or
        root_depth is None or
        irrigation_efficiency is None or
        target_yield_t_acre is None or
        not fertilizer_application_method or
        area_of_field_acre is None or
        age_years is None or
        plant_density_per_acre is None
    ):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing required fields'})
        }

    plot_uuid = str(uuid.uuid4())

    try:
        item = {
            "PK": user_id,
            "SK": f"PD-{plot_uuid}",
            "PlotId": plot_uuid,
            "type": "Plot Details",
            "Date": date,
            "Name": name,
            "latitude": latitude,
            "longitude": longitude,
            "CropType": crop_type,
            "Variety": variety,
            "SerialNumber": serial_number,
            "SoilType": soil_type,
            "PlotLocation": plot_location,
            "root_depth": root_depth,
            "Irrigation_efficiency": irrigation_efficiency,
            "target_yield_t_acre": target_yield_t_acre,
            "fertilizer_application_method": fertilizer_application_method,
            "area_of_field_acre": area_of_field_acre,
            "age_years": age_years,
            "plant_density_per_acre": plant_density_per_acre,
            "polygonPoints": polygon_points
        }

        table.put_item(Item=item)

        print("Saved successfully:", item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Plot saved successfully',
                'plotId': plot_uuid
            })
        }
    except Exception as e:
        print("Lambda Error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
