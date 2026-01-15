from fastapi import WebSocket
from app.chess.chess_match import ChessMatch
from app.chess.chess_match_http import ChessMatchHttp
from typing import Dict, Set
import asyncio

waiting_matches: Dict[str, ChessMatch] = {} 
matches: Dict[str, ChessMatch] = {}
waiting_creator_match: Dict[str, ChessMatch] = {}

waiting_matches_http: Dict[str, ChessMatchHttp]
matches_http: Dict[str, ChessMatchHttp]
# para enviar para o cliente

USERS: Dict[str, Dict[str, str]] = {}      # username -> { password }
SESSIONS: Dict[str, Dict] = {}   # token -> { user, exp }
USER_SESSIONS: Dict[str, Set] = {} # user -> {tokens}
ACTIVE_WS: Dict[str, Set[WebSocket]] = {}  # token -> set de WebSockets

match_lock = asyncio.Lock()