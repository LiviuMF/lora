from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from uvicorn.config import LOGGING_CONFIG

import secrets
from typing import Dict, Annotated, Optional

import config
from db import DatabaseClient
from data_cleaner import process_payload
from models import DeviceReadings, DeviceData


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
def fetch_records(
        appliance_id: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(verify_credentials)
        ],
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
) -> dict:
    if credentials:
        db_client = DatabaseClient()
        return {
            "results": db_client.fetch_records_for_appliance(
                appliance_id, from_date=from_date, to_date=to_date
            )
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )


@app.get("/records/{appliance_id}/latest")
def fetch_latest_records(
        appliance_id: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(verify_credentials)
        ]
) -> dict:
    if credentials:
        db_client = DatabaseClient()
        return {
            "results": db_client.fetch_records_last_24hours(
                appliance_id
            )
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
            sensor_data = process_payload(payload)
            db_client = DatabaseClient()
            db_client.save(DeviceReadings(**sensor_data))
            return f"Successfully received payload {sensor_data}"
        except:
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credentials are invalid"
        )


@app.post("/device")
async def post_device_data(
        credentials: Annotated[HTTPBasicCredentials, Depends(verify_credentials)],
        payload: Dict,
):
    if credentials:
        try:
            db_client = DatabaseClient()
            db_client.save(DeviceData(**payload))
            return f"Successfully received payload {payload}"
        except:
            pass
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credentials are invalid"
        )


@app.get("/records/devices")
def fetch_all_device_data(
        credentials: Annotated[
            HTTPBasicCredentials, Depends(verify_credentials)
        ]
) -> dict:
    if credentials:
        db_client = DatabaseClient()
        return {
            "results": db_client.fetch_all_device_data()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
        )
