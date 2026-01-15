from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uuid
import asyncio
from app.auth.session import *
from app.storage import *
from app.chess.chess_match import ChessMatch

router = APIRouter(tags=["match"])

templates = Jinja2Templates(directory="app/templates")

async def expire_match(match_id: str):
    await asyncio.sleep(60) # 60 segundos para o criador entrar na partida

    async with match_lock:
        match = waiting_creator_match.get(match_id)
        if match is None:
            return

        if match.status == "waiting":
            waiting_creator_match.pop(match_id, None)

#---------------
# CREATE MATCHES
@router.post("/create-math")
async def create_match_player(session: str | None = Cookie(default = None)):
    usr = get_user_from_session(session)
    if usr == None:
        response = RedirectResponse(
            url="/login",
            status_code=303
        )
        return response
    
    
    match_wait = ChessMatch(session, None)
    match_id = str(uuid.uuid4())

    #ia e em local diferente entao nao precisa ser verificado aqui
    while match_id in matches or match_id in waiting_matches:
        match_id = str(uuid.uuid4())

    waiting_creator_match[match_id] = match_wait
    asyncio.create_task(expire_match(match_id))

    return {"match_id" : match_id}
    
# ----------
# JOIN MATCH
@router.get("/match/{game_session}", response_class=HTMLResponse)
async def join_match(request: Request, game_session: str, session: str | None = Cookie(default = None)):
    usr = get_user_from_session(session)
    if not usr:
        return RedirectResponse("/login", status_code=303)

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
    