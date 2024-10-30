from datetime import datetime, timedelta


def process_payload(payload: dict) -> dict:
    current_timestamp: datetime = convert_timestamp_to_current_tz(
        payload["time"]
    )

    cleaned_data: dict = payload["object"]
    cleaned_data.update(
        {
            "dev_eui": payload["deviceInfo"]["devEui"],
            "timestamp": payload["time"],
            "current_time": current_timestamp.isoformat(),
            "date": current_timestamp.date().isoformat(),
            "time": current_timestamp.time().isoformat(),
        }
    )
    return {k.lower(): str(v) for k, v in cleaned_data.items()}


def convert_timestamp_to_current_tz(timestamp: str) -> datetime:
    _date: datetime = datetime.fromisoformat(timestamp).replace(tzinfo=None)
    tz_diff: timedelta = datetime.now() - _date
    hours: float = tz_diff.total_seconds() // 3600
    return _date + timedelta(hours=hours)
