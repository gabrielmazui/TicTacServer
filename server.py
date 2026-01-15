from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.routes import auth, home, match, websocket
from app.middleware.body_size import limit_body_size 
from app.middleware.rate_limit import rate_limit_middleware 
import asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(home.router)
app.include_router(match.router)
app.include_router(websocket.router)

MAX_CONCURRENT = 20
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

@app.middleware("http")
async def global_rate_limit(request: Request, call_next):
    async with semaphore:
        if request.url.path in ["/login", "/signup", "/logout"]:
            await asyncio.sleep(1)  
        else:
            await asyncio.sleep(0.3) 
        await limit_body_size(request)
        return await rate_limit_middleware(request, call_next)

