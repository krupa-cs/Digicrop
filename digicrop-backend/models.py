from pydantic import BaseModel, Field
import datetime
from typing import List, Optional


class SensorData(BaseModel):
    """
    Pydantic model representing a single sensor reading for a specific plot.
    """

    PK: str = Field(
        ...,
        description="Partition Key (Plot ID), e.g., PLOT#001",
        min_length=1,
    )

    SK: str = Field(
        ...,
        description="Sort Key, e.g., TS#2026-06-01",
        min_length=1,
    )

    date: datetime.date = Field(
        ...,
        description="Date of reading in YYYY-MM-DD format",
    )

    temp: float = Field(
        ...,
        description="Temperature in Celsius",
    )

    humidity: float = Field(
        ...,
        description="Humidity percentage",
        ge=0.0,
        le=100.0,
    )

    rainfall: float = Field(
        ...,
        description="Rainfall in mm",
        ge=0.0,
    )

    wind_speed: float = Field(
        ...,
        description="Wind speed in km/h",
        ge=0.0,
    )

    N: float = Field(
        ...,
        description="Nitrogen level",
        ge=0.0,
    )

    P: float = Field(
        ...,
        description="Phosphorus level",
        ge=0.0,
    )

    K: float = Field(
        ...,
        description="Potassium level",
        ge=0.0,
    )


class SensorDataResponse(BaseModel):
    """
    Response model for GET /api/v1/crop-sensor-data/{plot_id}
    """

    plot_id: str = Field(
        ...,
        description="The Plot ID",
    )

    timeseries: List[SensorData] = Field(
        ...,
        description="Chronologically sorted sensor readings",
    )

    latest_reading: Optional[SensorData] = Field(
        default=None,
        description="Most recent telemetry reading",
    )