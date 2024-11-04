from datetime import datetime, timedelta

import pandas as pd


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
    timestamp_cleaned = timestamp.split(".")[0]
    _date: datetime = datetime.fromisoformat(timestamp_cleaned).replace(tzinfo=None)
    tz_diff: timedelta = datetime.now() - _date
    hours: float = tz_diff.total_seconds() // 3600
    return _date + timedelta(hours=hours)


def create_df_for_plotting(df_data: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(df_data)
    df['tempc_ds'] = df['tempc_ds'].apply(lambda x: float(x))
    df['time'] = df['date'] + ' ' + df['time']
    df['time'] = pd.to_datetime(df['time'])
    return df
