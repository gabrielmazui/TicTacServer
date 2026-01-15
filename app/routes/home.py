from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.storage import *
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["home"])

#---------------
#HTMLResponse
@router.get("/")
def home(request: Request, session: str | None = Cookie(None)):
    ses = SESSIONS.get(session)
    if ses == None:
        response = RedirectResponse(
            url="/login",
            status_code=303
        )

    else:
        usr = ses.get("user") 
        response = templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "username": usr,
                "waiting_matches": waiting_matches,
                "running_matches": matches
            }
    )
    return response

@router.get("/login", response_class=HTMLResponse)
def login(request: Request, session: str | None = Cookie(None)):
    ses = SESSIONS.get(session)
    if ses == None:
        with open("app/templates/login.html", encoding="utf-8") as f:
            return f.read()

    else:
        response = RedirectResponse(
            url="/",
            status_code=303
        )
    return response

@router.get("/signup", response_class=HTMLResponse)
def signup(request: Request, session: str | None = Cookie(None)):
    ses = SESSIONS.get(session)
    if ses == None:
        with open("app/templates/signup.html", encoding="utf-8") as f:
            return f.read()

    else:
        response = RedirectResponse(
            url="/",
            status_code=303
        )
    return response