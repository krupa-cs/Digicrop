import json
import os
import tempfile
from typing import List, Dict, Any, Optional

DB_FILE = "plot_sensor_data.json"

def load_db() -> Dict[str, Any]:
    """
    Load the JSON database safely.
    Returns a dictionary. If the file doesn't exist, returns empty structure.
    """
    if not os.path.exists(DB_FILE):
        return {"timeseries": []}
    
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"timeseries": []}

def save_db(data: Dict[str, Any]) -> None:
    """
    Save the dictionary to the JSON database.
    Writes to a temporary file first and replaces the original atomically to prevent data corruption.
    """
    # Create a temporary file in the same directory as the target DB_FILE
    db_dir = os.path.dirname(os.path.abspath(DB_FILE))
    fd, temp_path = tempfile.mkstemp(dir=db_dir, suffix=".json")
    
    try:
        with os.fdopen(fd, 'w', encoding="utf-8") as temp_file:
            json.dump(data, temp_file, indent=2)
        
        # Atomically replace the old file with the new one
        os.replace(temp_path, DB_FILE)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def get_timeseries(plot_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all records for a specific plot_id (PK).
    Sorts chronologically by date.
    """
    data = load_db()
    records = [record for record in data.get("timeseries", []) if record.get("PK") == plot_id]
    
    # Sort by date
    records.sort(key=lambda x: x.get("date", ""))
    return records

def check_duplicate(pk: str, sk: str) -> bool:
    """
    Check if a record with the same PK and SK already exists.
    """
    data = load_db()
    for record in data.get("timeseries", []):
        if record.get("PK") == pk and record.get("SK") == sk:
            return True
    return False

def insert_record(record: Dict[str, Any]) -> None:
    """
    Append a new record to the timeseries database.
    """
    data = load_db()
    
    if "timeseries" not in data:
        data["timeseries"] = []
        
    data["timeseries"].append(record)
    save_db(data)
