from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid
from app.auth.session import *
from app.storage import *
from app.chess.chess_match import ChessMatch

app = APIRouter()

templates = Jinja2Templates(directory="app/templates")

#---------------
# CREATE MATCHES
@app.post("/create-math")
async def create_match_player(session: str | None = Cookie(default = None)):
    usr = get_user_from_session(session)
    if usr == None:
        response = RedirectResponse(
            url="/",
            status_code=303
        )
        return response
    
    
    match_wait = ChessMatch(session, None)
    match_id = str(uuid.uuid4())

    #ia e em local diferente entao nao precisa ser verificado aqui
    while match_id in matches or match_id in waiting_matches:
        match_id = str(uuid.uuid4())

    waiting_matches[match_id] = match_wait

    return {"match_id" : match_id}
    
# ----------
# JOIN MATCH
@app.get("/match/{game_session}", response_class=HTMLResponse)
async def join_match(request: Request, game_session: str, session: str | None = Cookie(default = None)):
    usr = get_user_from_session(session)
    if not usr:
        return RedirectResponse("/", status_code=303)

    if game_session not in waiting_matches and game_session not in matches:
        return templates.TemplateResponse(
            "match_not_found.html",
            {
                "request": request,
                "match_id": game_session,
                "username": usr
            }
        )

    template = "match.html" if game_session in waiting_matches else "spectate.html"

    return templates.TemplateResponse(
        template,
        {
            "request": request,
            "match_id": game_session,
            "username": usr
        }
    )
    