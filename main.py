from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import secrets
from typing import Annotated

from models import Temperature, DatabaseClient
import config


app = FastAPI()

security = HTTPBasic()


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
def post_temperature(
        credentials: Annotated[HTTPBasicCredentials, Depends(verify_credentials)],
        payload: Temperature
):
    if credentials:
        db_client = DatabaseClient()
        db_client.save(payload)
        return f"Successfully received payload {payload.__dict__}"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credentials are invalid"
        )

