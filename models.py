from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceReadings:
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

    class Meta:
        table_name = 'temperature'


@dataclass
class DeviceReadingsClientView:
    tempc_ds: str
    date: str
    time: str


@dataclass
class DeviceData:
    dev_eui: str
    dev_name: str
    dev_owner: str
    dev_owner_email: str

    class Meta:
        table_name = 'device_data'
