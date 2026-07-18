from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from models import SensorData, SensorDataResponse
import database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Digicrop Sensor API",
    description="A backend simulating a NoSQL database for agricultural sensor telemetry using a JSON file.",
    version="1.0.0"
)

@app.get("/api/v1/crop-sensor-data/{plot_id}", response_model=SensorDataResponse, status_code=status.HTTP_200_OK)
def get_sensor_data(plot_id: str):
    """
    Retrieve all timeseries data for a given plot_id.
    Data is sorted chronologically.
    Returns HTTP 404 if the plot is not found.
    """
    logger.info(f"Fetching sensor data for plot: {plot_id}")
    
    records = database.get_timeseries(plot_id)
    
    if not records:
        logger.warning(f"Plot {plot_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Plot ID '{plot_id}' not found."
        )
    
    latest_reading = records[-1] if records else None
    
    return SensorDataResponse(
        plot_id=plot_id,
        timeseries=records,
        latest_reading=latest_reading
    )

@app.post("/api/v1/crop-sensor-data", status_code=status.HTTP_201_CREATED)
def create_sensor_data(data: SensorData):
    """
    Ingest new sensor telemetry data.
    Validates input and prevents duplicate PK + SK entries.
    """
    logger.info(f"Ingesting data for PK: {data.PK}, SK: {data.SK}")
    
    try:
        # Check for duplicates
        if database.check_duplicate(data.PK, data.SK):
            logger.warning(f"Duplicate entry rejected: {data.PK} - {data.SK}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate record: Entry with PK '{data.PK}' and SK '{data.SK}' already exists."
            )
            
        # Convert date to string before saving to JSON
        record_dict = data.model_dump()
        record_dict['date'] = str(record_dict['date'])
        
        # Save record
        database.insert_record(record_dict)
        logger.info(f"Successfully ingested data for {data.PK}")
        return {"message": "Data successfully created"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Internal server error during ingestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the data."
        )
