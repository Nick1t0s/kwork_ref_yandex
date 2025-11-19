from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
import uvicorn
import database

app = FastAPI()

@app.get("/")
async def redirect_handler(request: Request, id: int):
    redirect_url = request.query_params.get("redirect")
    # Базовая проверка на валидность URL (опционально, но рекомендуется)
    parsed = urlparse(redirect_url)
    database.record_click(id)
    return RedirectResponse(url=redirect_url)


uvicorn.run(app, host="0.0.0.0", port=80)