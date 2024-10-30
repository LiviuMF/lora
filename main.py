from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from uvicorn.config import LOGGING_CONFIG

from datetime import datetime, timedelta
import secrets
from typing import Dict, Annotated

from db import DatabaseClient
from models import LHT65
import config


app = FastAPI()

security = HTTPBasic()

LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["access"][
    "fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'


def verify_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    provided_username = credentials.username.encode("utf8")
    correct_username = config.USERNAME.encode("utf8")
    is_correct_username = secrets.compare_digest(
        provided_username, correct_username
    )
    provided_password = credentials.password.encode("utf8")
    correct_password = config.PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        provided_password, correct_password
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
def status_check():
    return "Goliath Online"


@app.get("/records/{appliance_id}")
def fetch_records(appliance_id: str, credentials: Annotated[HTTPBasicCredentials, Depends(verify_credentials)]):
    if credentials:
        db_client = DatabaseClient()
        return {
            "results": db_client.fetch_by_id(appliance_id)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )


@app.post("/temp")
async def post_temperature(
        credentials: Annotated[HTTPBasicCredentials, Depends(verify_credentials)],
        payload: Dict,
):
    if credentials:
        try:
            sensor_data: dict = payload["object"]
            sensor_data.update(
                {
                    "dev_eui": payload["deviceInfo"]["devEui"],
                    "time": payload["time"],
                    "current_time": update_date_to_current_tz(payload["time"]),
                }
            )
            sensor_data = {k.lower(): str(v) for k, v in sensor_data.items()}
            db_client = DatabaseClient()
            db_client.save(LHT65(**sensor_data))
            return f"Successfully received payload {sensor_data}"
        except KeyError:
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credentials are invalid"
        )


def update_date_to_current_tz(date_str: str):
    _date = datetime.fromisoformat(date_str).replace(tzinfo=None)
    tz_diff: timedelta = datetime.now() - _date
    hours: float = tz_diff.total_seconds() // 3600
    return _date + timedelta(hours=hours)
