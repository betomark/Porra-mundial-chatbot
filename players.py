import json
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