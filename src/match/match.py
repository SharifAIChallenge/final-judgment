from match.judge import judge

class Match:
    def __init__(self,game_id,map_id,player_ids):
        self.players=player_ids
        self.game_id=game_id
        self.map_id=map_id

    def hold(self):
        judge(players=self.players,map_id=self.map_id,game_id=self.game_id)
        