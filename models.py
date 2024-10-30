from dataclasses import dataclass
import sqlite3
from typing import Optional


@dataclass
class LHT65:
    batv: float
    bat_status: float
    ext_sensor: str
    hum_sht: float
    tempc_ds: float
    tempc_sht: float
    dev_eui: str
    time: str
    current_time: Optional[str]
