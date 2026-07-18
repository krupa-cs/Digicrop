# Digicrop Backend

This is a complete production-quality backend solution for the Digicrop internship assignment using **FastAPI**. 
It simulates a NoSQL database for agricultural sensor telemetry using a local JSON file.

## Features
- RESTful APIs (`GET`, `POST`) for reading and writing sensor telemetry data.
- Built with **FastAPI** for high performance and automatic Swagger documentation.
- Robust data validation using **Pydantic**.
- NoSQL-like structured JSON database.
- Safe file-writing operations to prevent data corruption.
- Comprehensive error handling and HTTP status codes (200, 201, 400, 404, 409, 500).

---

## Project Structure

```text
digicrop-backend/
│── app.py                   # Main FastAPI application and API routes
│── database.py              # File I/O operations and simulated DB logic
│── models.py                # Pydantic models for data validation
│── plot_sensor_data.json    # The local JSON 'database'
│── requirements.txt         # Project dependencies
│── README.md                # Project documentation
│── .gitignore               # Ignored files for git
└── postman/
    └── Digicrop_API.postman_collection.json  # Postman testing collection
```

---

## Setup & Installation

Follow these steps to set up and run the project locally.

### 1. Virtual Environment Setup

Create a virtual environment to manage dependencies cleanly:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependency Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Running the Server

Start the FastAPI application using Uvicorn with auto-reload enabled:

```bash
uvicorn app:app --reload
```

The server will start at `http://127.0.0.1:8000`.

---

## API Documentation

FastAPI automatically generates interactive Swagger documentation. Once the server is running, visit:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## API Endpoints

### 1. Get Plot Timeseries
Retrieve chronologically sorted sensor telemetry data for a specific plot.

- **Endpoint:** `GET /api/v1/crop-sensor-data/{plot_id}`
- **Path Parameter:** `plot_id` (e.g., `PLOT#001`)

**Sample Request (Success):**
```bash
curl -X 'GET' 'http://127.0.0.1:8000/api/v1/crop-sensor-data/PLOT#001' -H 'accept: application/json'
```

**Sample Response (200 OK):**
```json
{
  "plot_id": "PLOT#001",
  "timeseries": [
    {
      "PK": "PLOT#001",
      "SK": "TS#2026-06-01",
      "date": "2026-06-01",
      "temp": 32.5,
      "humidity": 65.0,
      "rainfall": 12.0,
      "wind_speed": 14.2,
      "N": 45.0,
      "P": 30.0,
      "K": 60.0
    }
  ],
  "latest_reading": {
    "PK": "PLOT#001",
    "SK": "TS#2026-06-01",
    "date": "2026-06-01",
    "temp": 32.5,
    "humidity": 65.0,
    "rainfall": 12.0,
    "wind_speed": 14.2,
    "N": 45.0,
    "P": 30.0,
    "K": 60.0
  }
}
```

**Sample Response (404 Not Found):**
```json
{
  "detail": "Plot ID 'INVALID' not found."
}
```

---

### 2. Ingest Sensor Data
Ingest new sensor telemetry data into the JSON database.

- **Endpoint:** `POST /api/v1/crop-sensor-data`

**Sample Request (Success):**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/crop-sensor-data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "PK": "PLOT#001",
  "SK": "TS#2026-06-03",
  "date": "2026-06-03",
  "temp": 34.0,
  "humidity": 60.5,
  "rainfall": 0.0,
  "wind_speed": 15.1,
  "N": 43.0,
  "P": 28.5,
  "K": 58.0
}'
```

**Sample Response (201 Created):**
```json
{
  "message": "Data successfully created"
}
```

**Sample Response (409 Conflict - Duplicate Record):**
```json
{
  "detail": "Duplicate record: Entry with PK 'PLOT#001' and SK 'TS#2026-06-03' already exists."
}
```

**Sample Response (422 Unprocessable Entity - Validation Error):**
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "humidity"],
      "msg": "Input should be less than or equal to 100",
      "input": 150.0
    }
  ]
}
```

---

## Screenshots Placeholder

![Swagger API Docs Placeholder](https://via.placeholder.com/800x400.png?text=Swagger+UI+Documentation)
*Screenshot: FastAPI automatically generated Swagger UI documentation showing the available routes.*

---

## Testing

A Postman collection is included in the `/postman` directory. 
1. Open Postman.
2. Click **Import**.
3. Select `postman/Digicrop_API.postman_collection.json`.
4. Run the pre-configured API requests.

## Future Improvements
- **Database Migration**: Migrate from JSON files to a real NoSQL database like MongoDB or DynamoDB for true scalability and concurrency support.
- **Authentication**: Add JWT token-based authentication to secure the API.
- **Unit Tests**: Add a suite of unit and integration tests using `pytest` and `httpx`.
- **Dockerization**: Containerize the application with Docker for seamless deployment across environments.
