from app.chess.chess_match import ChessMatch

waiting_matches: dict[str, ChessMatch] = {} 
matches: dict[str, ChessMatch] = {} 
# id -> class do match

users = {}      # username -> { password }
sessions = {}   # token -> { user, exp }