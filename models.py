from dataclasses import dataclass
from typing import Optional


@dataclass
class LHT65:
    batv: str
    bat_status: str
    ext_sensor: str
    hum_sht: str
    tempc_ds: str
    tempc_sht: str
    dev_eui: str
    timestamp: str
    current_time: Optional[str]
    date: str
    time: str


@dataclass
class LHTClientView:
    tempc_ds: str
    date: str
    time: str