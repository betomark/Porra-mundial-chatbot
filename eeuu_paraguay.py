import teams

eeuu = teams.Team(team_id=4724, name="United States")
paraguay = teams.Team(team_id=4789, name="Paraguay")

eeuu_stats = eeuu.get_team_summary_stats_by_year(year=2026, store=True)
paraguay_stats = paraguay.get_team_summary_stats_by_year(year=2026, store=True)