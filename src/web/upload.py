import os
import uuid
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ..bot.core.storage import WEBHOOK_DOMAIN

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

ALLOWED_IPS = {"127.0.0.1"} 
API_TOKEN = "broodskoye"
api_key_header = APIKeyHeader(name="X-Auth-Token")

async def remove_file_after_delay(path: str, delay: int):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)
        print(f"Файл {path} успешно выпилен.")

def verify_token(token: str = Depends(api_key_header)):
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_ip(request: Request):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail=f"IP {client_ip} not allowed for uploads")

@app.post("/upload")
@limiter.limit("5/minute")
async def upload_file(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    _ = Depends(verify_token),
    __ = Depends(verify_ip)
):
    if not file.filename.endswith((".html", ".txt")):
        raise HTTPException(status_code=400, detail="Only HTML or TXT allowed")

    unique_filename = f"{uuid.uuid4()}.html"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    background_tasks.add_task(remove_file_after_delay, file_path, 600)
    
    return f"https://{WEBHOOK_DOMAIN}/it-top_bot/files/{unique_filename}"