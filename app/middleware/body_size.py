from fastapi import Request, HTTPException

MAX_BODY_SIZE = 1024 * 1024  # 1MB

async def limit_body_size(request: Request):
    content_length = request.headers.get("content-length")

    if content_length is None:
        return

    if int(content_length) > MAX_BODY_SIZE:
        raise HTTPException(
            status_code=413,
            detail="payload too large"
        )