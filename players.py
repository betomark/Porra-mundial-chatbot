import utils.sofascore_client
import urls

class Player:
    def __init__(self, player_id):
        self.player_id = player_id  

    def get_player_seasons(self):
        url = urls.PLAYER_SEASONS.format(player_id=self.player_id)
        sofascore_client = utils.sofascore_client.SofascoreClient()
        return sofascore_client.get(url)

    def get_player_season_stats(self, tournament_id, season_id):
        url = urls.PLAYER_SEASON_STATS.format(player_id=self.player_id, tournament_id=tournament_id, season_id=season_id)
        sofascore_client = utils.sofascore_client.SofascoreClient()
        return sofascore_client.get(url)

    def get_player_total_stats(self):
        player_seasons = self.get_player_seasons()
        player_stats = {}
        for tournament in player_seasons["uniqueTournamentSeasons"]:
            tournament_id = tournament["uniqueTournament"]["id"]
            tournament_name = tournament["uniqueTournament"]["name"]
            tournament_place = tournament["uniqueTournament"]["category"]["name"]
            player_stats[tournament_name] = {
                "tournament_id": tournament_id,
                "tournament_place": tournament_place,
                "seasons": {}
            }
            for season in tournament["seasons"]:
                season_id = season["id"]
                season_name = season["name"]
                season_year = season["year"]
                player_stats[tournament_name]["seasons"][season_name] = {
                    "season_id": season_id,
                    "season_year": season_year
                }
                player_stats[tournament_name]["seasons"][season_name] = self.get_player_season_stats(tournament_id, season_id)

        return player_stats
    
    def get_player_stats_by_natural_year(self, year):
        pass

    def get_player_stats_by_season(self, season_name):
        pass

    def get_player_stats_by_tournament(self, tournament_name):
        pass

    def get_player_stats_by_tournament_and_season(self, tournament_name, season_name):
        pass

    def get_player_stats_by_league_adjusted(self, league_name):
        pass

    def store_player_stats(self, player_stats):
        pass