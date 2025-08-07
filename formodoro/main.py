import json
import os
from datetime import datetime
from json import JSONDecodeError

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from notifiers import notify
import requests
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from starlette.datastructures import FormData
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from .db import insert_data

# Initialize app and rate limiter
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(HTTP_429_TOO_MANY_REQUESTS, _rate_limit_exceeded_handler)


# CORS setup: only allow your frontend domain
origins = os.environ.get("CORS_ORIGINS", "https://yourfrontend.com").split(",")
print(f"Allowed origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

notify_provider = os.environ.get("NOTIFIERS_PROVIDER", "telegram")


# parse both formdata and json data
async def get_body(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type is None:
        raise HTTPException(status_code=400, detail="No Content-Type provided!")
    elif content_type == "application/json":
        try:
            return await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON data")
    elif content_type == "application/x-www-form-urlencoded" or content_type.startswith("multipart/form-data"):
        try:
            return await request.form()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid Form data")
    else:
        raise HTTPException(status_code=400, detail="Content-Type not supported!")


@app.post("/submit")
@limiter.limit(os.environ.get("RATELIMIT", "5/minute"))
def main(
    body=Depends(get_body),
    redirect: str = "",
    request: Request = None,
    referer: str = Header(default=None),
    origin: str = Header(default=None),
):

    # print environment variables
    print("Environment Variables:")
    for key, value in os.environ.items():
        print(f"{key}: {value}")

    # Check Referer or Origin to validate request source
    if not any(
        (referer and referer.startswith(domain)) or (origin and origin.startswith(domain)) for domain in origins
    ):
        print(f"Invalid request source: {referer} or {origin}")
        raise HTTPException(status_code=403, detail="Invalid request source")

    if isinstance(body, dict):  # if JSON data received
        data = body
    elif isinstance(body, FormData):  # if Form/File data received
        body_dict = {key: body[key] for key in body.keys()}
        data = body_dict
    else:
        raise HTTPException(status_code=400, detail="Unsupported data type")

    try:
        if notify_provider == "n8n":
            n8n_webhook = os.environ.get("N8N_WEBHOOK")
            n8n_auth_header = os.environ.get("N8N_AUTH_HEADER")
            n8n_auth_header_name = os.environ.get("N8N_AUTH_HEADER_NAME", "Authorization")
            if not n8n_webhook or not n8n_auth_header:
                raise Exception("N8N_WEBHOOK or N8N_AUTH_HEADER not set in environment")
            headers = {n8n_auth_header_name: n8n_auth_header, "Content-Type": "application/json"}
            resp = requests.post(n8n_webhook, headers=headers, data=json.dumps(data))
            if not resp.ok:
                raise Exception(f"n8n webhook error: {resp.status_code} {resp.text}")
        else:
            notify(notify_provider, message=f"New submission received:\n {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Notification error: {e}")

    try:
        data["timestamp"] = datetime.now().isoformat()  # Add current timestamp
        insert_data(data)  # Insert data into the database
        data.pop("_id", None)  # Remove MongoDB ObjectId from response if present
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500,
        )
    if redirect:
        return RedirectResponse(url=redirect, status_code=302)
    return JSONResponse(content={"status": "success", "data": data})
