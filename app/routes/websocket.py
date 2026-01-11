from fastapi import APIRouter,WebSocket, WebSocketDisconnect, Cookie
from storage import *
import asyncio

match_lock = asyncio.Lock()

app = APIRouter()

@app.websocket("/ws/match/{match_id}")
async def ws_match(
    websocket: WebSocket,
    match_id: str,
    session: str | None = Cookie(default=None)
):
    await websocket.accept()

    usr = users.get(session, None)
    if usr == None:
        await websocket.send_json({
            "type": "error",
            "content": "user does not exist"
        })
        await websocket.close()
        return

    match = None
    #isso ta errado eu acho imagina quand o primeiro entrar
    async with match_lock:
        if match_id in waiting_matches:
            match = waiting_matches.pop(match_id)
            matches[match_id] = match
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
    
    match.connections.append(websocket)

    player = False # se e jogador ou spectador
    #desnecssario tlvz
    if match.players["white"] == usr:
        # valor dado quando /create-match
        player = True
    elif match.match.players["black"] == None:
        # vai ser jogador
        player = True
        match.players["black"] = usr
        match.status = "playing"

    if not player:
        match.spectators += 1

    try:
        while True:
            data = await websocket.receive_json()
            type = data.get("type", None)

            if type == "move":
                if match.status == "waiting":
                    await websocket.send_json({
                        "type": "error",
                        "content": "waiting for a player to join the match"
                    })
                    continue

                elif match.status == "finished":
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

                turn = match.turn
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

                    if match.move((fr, fc), (tr, tc)):
                        # brodcast
                        for ws in match.connections:
                            await ws.send_json({
                                "type": "move",
                                "board": match.board
                            })
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

                await websocket.send_json({
                    "type": "error",
                    "content": "could not move that"
                })
    except WebSocketDisconnect:
        #verificar se era jogador
        if not player:
            match.spectators -= 1
        else:
            if match.players["dark"] == None:
                # a partida nem comecou
                waiting_matches.pop(match_id, None)
                return
            
            match.status = "finished"
            winner = "unknown" 
            if match.players["white"] == player:
                winner = users.get(match.players["dark"], None)

            elif match.players["dark"] == player:
                winner = users.get(match.players["white"], None)

            # brodcast
            for ws in match.connections:
                await ws.send_json({
                    "type": "end",
                    "winner": winner
                })
                ws.close()

            matches.pop(match_id, None)
            #partida acabou
            
        return