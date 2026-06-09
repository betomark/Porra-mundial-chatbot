SOFASCORE_BASE_URL = "https://www.sofascore.com/api/v1"

#tournament endpoints
STANDINGS = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/season/{{season_id}}/standings/total"
EVENTS = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/scheduled-events/{{date}}"
POWER_RANKINGS_ROUNDS = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/season/{{season_id}}/power-rankings/rounds"
TEAMS_POWER_RANKINGS_ROUNDS = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/season/{{season_id}}/power-rankings/round/{{round}}"

#match endpoints
MATCH_ODDS = f"{SOFASCORE_BASE_URL}/event/{{event_id}}/odds/1/all"
MATCH_LINEUPS = f"{SOFASCORE_BASE_URL}/event/{{event_id}}/lineups"
MATCH_VOTES = f"{SOFASCORE_BASE_URL}/event/{{event_id}}/votes"
MATCH_STATS = f"{SOFASCORE_BASE_URL}/event/{{event_id}}/statistics"
RANKING = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/season/{{season_id}}/power-rankings/round/{{round_id}}"

#team endpoints
TEAM_SEASONS = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/player-statistics/seasons"
TEAM_STANDINGS = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/standings/seasons"
TEAM_LASTS_MATCHES = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/events/last/0"
TEAM_RECENT_PERFORMANCE = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/performance"
TEAM_STATS = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/unique-tournament/{{tournament_id}}/season/{{season_id}}/statistics/overall"
SQUAD = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/players"

#player endpoints
PLAYER_SEASONS = f"{SOFASCORE_BASE_URL}/player/{{player_id}}/statistics/seasons"
PLAYER_SEASON_STATS = f"{SOFASCORE_BASE_URL}/player/{{player_id}}/unique-tournament/{{tournament_id}}/season/{{season_id}}/statistics/overall"

#league endpoints
LEAGUE_POWER_RANKINGS = "https://dataviz.theanalyst.com/opta-power-rankings/league-meta.json"