import time
from fastapi import Request, HTTPException

requests_per_ip = {}

MAX_REQUESTS = 20        
WINDOW_SECONDS = 10     

async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    # pega histórico do IP
    history = requests_per_ip.get(ip, [])

    # remove requisições antigas
    history = [t for t in history if now - t < WINDOW_SECONDS]

    if len(history) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="A lot of requests"
        )

    history.append(now)
    requests_per_ip[ip] = history

    response = await call_next(request)
    return response
