from fastapi import APIRouter, Cookie, Form, HTTPException, Response
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from app.auth.session import *
from app.storage import *

router = APIRouter(tags=["auth"])
pwd = CryptContext(schemes=["argon2"], deprecated="auto")

#-------------
# SIGNUP
@router.post("/signup")
async def signup(
    username: str = Form(..., min_length=3, max_length=20),
    password: str = Form(..., min_length=6, max_length=128),
    session: str | None = Cookie(None)
):
    
    usr = get_user_from_session(session)
    if usr is not None:
        return RedirectResponse(url="/", status_code=303)
    
    if username in USERS:
        raise HTTPException(400, "User already exists")

    USERS[username] = {
        "password": pwd.hash(password)
    }

    response = RedirectResponse(
        url="/login",
        status_code=303
    )
    return response


@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    keeplogged: str | None = Form(None),
    session: str | None = Cookie(None)
):
    usr = get_user_from_session(session)
    if usr is not None:
        return RedirectResponse(url="/", status_code=303)
    
    user = USERS.get(username, None)

    if not user or not pwd.verify(password, user["password"]):
        raise HTTPException(401, "Incorrect user or password")

    session_time = 60 * 60           # 1 hora
    if keeplogged:
        session_time = 60 * 60 * 24 * 7  # 7 dias
    token = create_session(username, session_time)

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax"
    )
    
    return response

@router.post("/logout")
async def logout(
    response: Response,
    session: str | None = Cookie(None)
):
    usr = get_user_from_session(session)

    if not usr:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    
    await logout_all_ws(usr)

    response = RedirectResponse(
        url="/login",
        status_code=303
    )

    response.delete_cookie("session")
    return response