from fastapi import APIRouter,WebSocket, WebSocketDisconnect, Cookie
from app.storage import *
from app.chess.chess_match import ChessMatch
from app.chess.chess_match_http import ChessMatchHttp

router = APIRouter(tags=["ws"])

@router.websocket("/ws/match/{match_id}")
async def ws_match(
    websocket: WebSocket,
    match_id: str,
    session: str | None = Cookie(default=None)
):
    await websocket.accept()

    ses = SESSIONS.get(session)
    
    if ses == None:
        await websocket.send_json({
            "type": "error",
            "content": "user does not exist"
        })
        await websocket.close()
        return

    match = None
   

    usr = ses.get("user")
    
    async with match_lock:
        if match_id in waiting_creator_match:
            match = waiting_creator_match[match_id]
        if match_id in waiting_matches:
            match = waiting_matches[match_id]
        elif match_id in matches:
            match = matches[match_id]
        

    if match == None:
        # partida nao existe
        await websocket.send_json({
            "type": "error",
            "content": "match does not exist"
        })
        await websocket.close()
        return
    

    async with match_lock:
        if session not in ACTIVE_WS:
            ACTIVE_WS[session] = set()
        ACTIVE_WS[session].add(websocket)

        match.connections.append(websocket)
        
    player = False # se e jogador ou spectador
    
    if match.players["white"] == usr:
        
        async with match_lock:
            player = True
            match.creator_connected = True
            waiting_creator_match.pop(match_id, None)
            waiting_matches[match_id] = match
            waiting_matches_http[match_id] = ChessMatchHttp(match_id, usr, None)

            # apenas por precaucao
            if match.opponent_connected:
                match.status = "playing"

    elif match.players["black"] == None:
        # vai ser jogador
        async with match_lock:
            player = True
            match.players["black"] = usr
            match.opponent_connected = True

            if match.creator_connected:
                match.status = "playing"
                waiting_matches.pop(match_id, None)
                matches[match_id] = match

                m = waiting_matches_http.pop(match_id, None)
                if m:
                    m.players[1] = usr
                    matches_http[match_id] = m
    
    async with match_lock:
        if not player:
            match.spectators += 1
            match_http = matches_http.get(match_id)
            if match_http:
                match_http.spectators += 1

    try:
        while True:
            data = await websocket.receive_json()
            async with match_lock:
                status = match.status
            
            type = data.get("type", None)

            if type == "move":
                if status == "waiting":
                    await websocket.send_json({
                        "type": "error",
                        "content": "waiting for a player to join the match"
                    })
                    continue

                elif status == "finished":
                    await websocket.send_json({
                        "type": "error",
                        "content": "this game already finished"
                    })
                    continue

                if not player:
                    await websocket.send_json({
                        "type": "error",
                        "content": "you are not a player"
                    })
                    continue
                
                async with match_lock:
                    turn = match.engine.turn
                if match.players[turn] == usr:
                    fr = data.get("fr", None)
                    fc = data.get("fc", None)
                    tr = data.get("tr", None)
                    tc = data.get("tc", None)
                    if fr == None or fc == None or tr == None or tc == None:
                        await websocket.send_json({
                            "type": "error",
                            "content": "error while reading positions"
                        })
                        continue
                    
                    async with match_lock:
                        moved = match.engine.move((fr, fc), (tr, tc))
                        board = match.engine.board
                        turn = match.engine.turn
                        check = match.engine.is_in_check(turn)
                        checkmate = match.engine.is_checkmate(turn)

                    if moved:
                        # brodcast
                        async with match_lock:
                            connections = list(match.connections)

                        for ws in connections:
                            try:
                                await ws.send_json({
                                    "type": "move",
                                    "board": board,
                                    "turn": turn,
                                    "check": check,
                                    "checkmate": checkmate
                                })
                            except:
                                match.connections.remove(ws)
                                
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "content": "could not move that"
                        })
                        continue
                else:   
                    await websocket.send_json({
                        "type": "error",
                        "content": "it is not your turn"
                    })
                    continue

    except WebSocketDisconnect:
        #verificar se era jogador
        async with match_lock:
            if session in ACTIVE_WS:
                ACTIVE_WS[session].remove(websocket)
            if websocket in match.connections:
                match.connections.remove(websocket)

            if not player:
                match.spectators = max(0, match.spectators - 1)
                match_http = matches_http.get(match_id)
                if match_http:
                    match_http.spectators = max(0, match_http.spectators - 1)

            else:
                if match.status == "waiting":
                    # a partida nem comecou
                    
                    waiting_matches.pop(match_id, None)
                    waiting_matches_http.pop(match_id, None)
                    return
                
                match.status = "finished"
                winner = "unknown" 
                if match.players["white"] == usr:
                    sess = SESSIONS.get(match.players["black"])
                    if sess != None:
                        winner = sess.get("user")

                elif match.players["black"] == usr:
                    sess = SESSIONS.get(match.players["white"])
                    if sess != None:
                        winner = sess.get("user")

                if winner == None:
                    winner = "Unknown"
                # brodcast
            async with match_lock:
                connections = list(match.connections)
                creator_connected = match.creator_connected
            for ws in connections:
                try:
                    if creator_connected:
                        await ws.send_json({
                            "type": "end",
                            "winner": winner
                        })
                    else:
                        await ws.send_json({
                            "type": "match_error",
                            "error": "the match exceed the time limit or the match create could not join"
                        })
                    ws.close()
                except:
                    async with match_lock:
                        match.connections.remove(ws)

            async with match_lock:
                matches.pop(match_id, None)
                matches_http.pop(match_id, None)
                #partida acabou
        return
    

@router.websocket("/ws/session")
async def ws_session(websocket: WebSocket, session: str | None = Cookie(default=None)):
    await websocket.accept()

    # valida sessão
    if not session or session not in SESSIONS:
        await websocket.close(code=1008)  # Policy Violation
        return

    # registra WS
    if session not in ACTIVE_WS:
        ACTIVE_WS[session] = set()
    ACTIVE_WS[session].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ACTIVE_WS.get(session, set()).discard(websocket)