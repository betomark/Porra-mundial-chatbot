import utils.sofascore_client
import urls

def get_player_seasons(player_id):
    url = urls.PLAYER_SEASONS.format(player_id=player_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    return sofascore_client.get(url)

def get_player_season_stats(player_id, tournament_id, season_id):
    url = urls.PLAYER_SEASON_STATS.format(player_id=player_id, tournament_id=tournament_id, season_id=season_id)
    sofascore_client = utils.sofascore_client.SofascoreClient()
    return sofascore_client.get(url)

def get_player_total_stats(player_id):
    player_seasons = get_player_seasons(player_id)
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
            player_stats[tournament_name]["seasons"][season_name] = get_player_season_stats(player_id, tournament_id, season_id)

    return player_stats