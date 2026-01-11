from fastapi import WebSocket
from typing import List

class ChessMatch:
    def __init__(self, white_player, black_player):
        # jogadores
        self.players = {
            "white": white_player,
            "black": black_player
        }
        
        # estado do jogo
        self.board = self._create_initial_board()
        self.turn = "white"
        self.status = "waiting"   # playing waiting finished
        self.spectators = 0
        self.move_history = []
        self.connections: List[WebSocket] = []


    def _create_initial_board(self):
        return [
            ["r","n","b","q","k","b","n","r"],
            ["p","p","p","p","p","p","p","p"],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["","","","","","","",""],
            ["P","P","P","P","P","P","P","P"],
            ["R","N","B","Q","K","B","N","R"],
        ]

    def move(self, from_pos, to_pos):
        if self.status != "playing":
            return False

        fr, fc = from_pos
        tr, tc = to_pos

        piece = self.board[fr][fc]
        if piece == "":
            return False

        # confere turno
        if self.turn == "white" and not piece.isupper():
            return False
        if self.turn == "black" and not piece.islower():
            return False

        # valida movimento
        if not self._is_valid_move(piece, from_pos, to_pos):
            return False

        # executa movimento
        self.board[tr][tc] = piece
        self.board[fr][fc] = ""
        self.move_history.append((from_pos, to_pos, piece))

        # troca turno
        self.turn = "black" if self.turn == "white" else "white"
        return True

    # -------------------------
    # VALIDAÇÃO GERAL
    # -------------------------
    def _is_valid_move(self, piece, from_pos, to_pos):
        piece_type = piece.lower()

        if piece_type == "p":
            return self._valid_pawn_move(piece, from_pos, to_pos)
        if piece_type == "r":
            return self._valid_rook_move(from_pos, to_pos)
        if piece_type == "n":
            return self._valid_knight_move(from_pos, to_pos)
        if piece_type == "b":
            return self._valid_bishop_move(from_pos, to_pos)
        if piece_type == "q":
            return self._valid_queen_move(from_pos, to_pos)
        if piece_type == "k":
            return self._valid_king_move(from_pos, to_pos)

        return False

    # -------------------------
    # REGRAS DAS PEÇAS
    # -------------------------
    def _valid_pawn_move(self, piece, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos

        direction = -1 if piece.isupper() else 1

        # andar pra frente
        if fc == tc and self.board[tr][tc] == "":
            if tr == fr + direction:
                return True

        # captura diagonal
        if abs(tc - fc) == 1 and tr == fr + direction:
            target = self.board[tr][tc]
            if target != "" and target.isupper() != piece.isupper():
                return True

        return False

    def _valid_rook_move(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos

        if fr != tr and fc != tc:
            return False

        return self._path_clear(from_pos, to_pos)

    def _valid_knight_move(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos

        return (abs(fr - tr), abs(fc - tc)) in [(1, 2), (2, 1)]

    def _valid_bishop_move(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos

        if abs(fr - tr) != abs(fc - tc):
            return False

        return self._path_clear(from_pos, to_pos)

    def _valid_queen_move(self, from_pos, to_pos):
        return (
            self._valid_rook_move(from_pos, to_pos)
            or self._valid_bishop_move(from_pos, to_pos)
        )

    def _valid_king_move(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos

        return abs(fr - tr) <= 1 and abs(fc - tc) <= 1

    
    def _path_clear(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos

        step_r = (tr - fr) and (1 if tr > fr else -1)
        step_c = (tc - fc) and (1 if tc > fc else -1)

        r, c = fr + step_r, fc + step_c
        while (r, c) != (tr, tc):
            if self.board[r][c] != "":
                return False
            r += step_r
            c += step_c

        return True
