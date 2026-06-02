SOFASCORE_BASE_URL = "https://www.sofascore.com/api/v1"

STANDINGS = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/season/{{season_id}}/standings/total"
EVENTS = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/scheduled-events/{{date}}"
RANKING = f"{SOFASCORE_BASE_URL}/unique-tournament/{{tournament_id}}/season/{{season_id}}/power-rankings/round/{{round_id}}"
TEAM_LASTS_MATCHES = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/events/last/0"
TEAM_RECENT_PERFORMANCE = f"{SOFASCORE_BASE_URL}/team/{{team_id}}/performance"