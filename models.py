from dataclasses import dataclass
from datetime import datetime
import sqlite3
from typing import Optional


@dataclass
class Temperature:
    appliance_id: str
    temperature: float
    timestamp: Optional[str] = datetime.now().strftime("%Y%m%d%H%M%S")


class DatabaseClient:
    conn = sqlite3.connect('temperature.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS '
        'temperature (timestamp TEXT, appliance_id TEXT, temperature REAL)'
    )

    def fetch_by_id(self, appliance_id: str):
        sql_query = f"SELECT * FROM temperature WHERE appliance_id = '{appliance_id}'"
        rows = self.cursor.execute(sql_query)
        return [Temperature(**row) for row in rows]

    def save(self, temperature: Temperature):
        appliance_id, temperature, timestamp = temperature.__dict__.values()
        sql_query = (
                    "INSERT INTO temperature (timestamp, appliance_id, temperature)"
                    f"VALUES({timestamp}, '{appliance_id}', {temperature});"
        )
        self.cursor.execute(sql_query)
        self.conn.commit()
