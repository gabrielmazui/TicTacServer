import time, secrets
from app.storage import SESSIONS, USER_SESSIONS, ACTIVE_WS
import asyncio

def logout(token: str):
    user = SESSIONS.pop(token, None)
    if user:
        USER_SESSIONS[user["user"]].discard(token)

def logout_all(username: str):
    tokens = list(USER_SESSIONS.get(username, set()))
    for token in tokens:
        SESSIONS.pop(token, None)
    USER_SESSIONS[username] = set()

async def logout_all_ws(username: str):
    tokens = list(USER_SESSIONS.get(username, set()))

    logout_all(username)

    for token in tokens:
        websockets_set = ACTIVE_WS.get(token, set())
        for ws in list(websockets_set):
            try:
                await ws.send_text("logout")  # avisa cliente
                await ws.close(code=1008)      # fecha WS
            except:
                pass
        ACTIVE_WS[token] = set()  # limpa WS desse token


def create_session(username: str, SESSION_TIME: int = 60 * 60):
    token = secrets.token_hex(32)
    SESSIONS[token] = {
        "user": username,
        "exp": time.time() + SESSION_TIME
    }
    
    if username not in USER_SESSIONS:
        USER_SESSIONS[username] = set()
    USER_SESSIONS[username].add(token)
    return token


def get_user_from_session(token: str | None):
    if not token:
        return None

    data = SESSIONS.get(token)
    if not data:
        return None

    if data["exp"] < time.time():
        # remove sessão expirada
        logout(token)
        return None

    return data["user"]