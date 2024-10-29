from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from uvicorn.config import LOGGING_CONFIG

import secrets
from typing import Dict, Annotated

from models import DatabaseClient, LHT65
import config


app = FastAPI()

security = HTTPBasic()

LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"

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
        results = db_client.fetch_by_id(appliance_id)
        return {"results": results}
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
            sensor_data = payload["object"]
            sensor_data.update(
                {
                    "dev_eui": payload["deviceInfo"]["devEui"],
                    "time": payload["time"]
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

