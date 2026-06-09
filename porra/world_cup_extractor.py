import os
import json
import time
import logging
from selenium import webdriver
from porra import players, teams, events
from datafc.utils import SofascoreClient
from utils.logging_config import setup_logging
from utils.mongo_client import MongoDBClient
from utils.persistence import persist

setup_logging()
logger = logging.getLogger(__name__)


def create_chrome_driver():
    """Create and configure a Chrome WebDriver instance for extraction."""
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-infobars")

    if os.getenv("HEADLESS", "false").lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")

    # Enable performance logging so `driver.get_log("performance")` works
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    return webdriver.Chrome(options=options)


def run_extractor():
    """Execute the full World Cup extraction workflow and persist extracted data."""
    logger.info("🚀 Starting browser...")
    driver = create_chrome_driver()
    # mongo = MongoDBClient()
    team_list = []

    try:
        logger.info("🌐 Loading Sofascore...")
        driver.get("https://www.sofascore.com/es/football/tournament/world/world-championship/16#id:58210")

        # Wait for the page to load and interact
        time.sleep(2)
        logger.info("📜 Scrolling...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        logger.info("🔍 Inspecting network traffic and extracting data...")
        logs_raw = driver.get_log("performance")
        for entry in logs_raw:
            log = json.loads(entry["message"])["message"]
            print(log)
            # This time we look for "Network.responseReceived" (when the response has already arrived in the browser)
            if log["method"] == "Network.responseReceived":
                params = log["params"]
                response = params["response"]
                url = response["url"]

                # Filter only calls that target the Sofascore API
                if "sofascore.com/api/v1/unique-tournament/16/scheduled-events/" in url or "sofascore.com/api/v1/unique-tournament/16/season/58210/standings/total" in url or "sofascore.com/api/v1/unique-tournament/16/season/58210/power-rankings" in url:
                    request_id = params["requestId"]

                    try:
                        # Ask Chrome for the body of that specific response using its ID
                        body_data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})

                        # body_data['body'] contains the JSON payload as plain text
                        response_text = body_data["body"]
                        data_dict = json.loads(response_text)
                        keys = data_dict.keys()
                        logger.info(f"✅ Extracted data from {url} with keys: {keys}")
                        if "standings" in keys:
                            logger.info("📊 Saving standings...")
                            persist(
                                collection="standings",
                                mongo_doc={
                                    "_id": "world_cup_2026_standings",
                                    "reference": "world_cup_2026",
                                    "data": data_dict,
                                },
                                json_path="data/standings.json",
                                json_data=data_dict,
                                filter_fields=["_id"],
                            )
                            logger.info("📋 Extracting team data for future lookup...")
                            team_list = teams.get_teams(data_dict, store=True)
                            logger.info(f"👥 Extracted teams: {[team.name for team in team_list]}")
                        elif "powerRankings" in keys:
                            logger.info("📈 Saving power rankings...")
                            persist(
                                collection="power_rankings",
                                mongo_doc={
                                    "_id": "world_cup_2026_power_rankings",
                                    "reference": "world_cup_2026",
                                    "data": data_dict,
                                },
                                json_path="data/power_rankings.json",
                                json_data=data_dict,
                                filter_fields=["_id"],
                            )
                        elif "events" in keys:
                            logger.info("📅 Saving scheduled events...")
                            for event in data_dict["events"]:
                                home_team = event["homeTeam"]["name"]
                                away_team = event["awayTeam"]["name"]
                                logger.info(f"   - {home_team} vs {away_team} at {event['startTimestamp']}")
                                output_filename = f"data/events/scheduled_event_{home_team} vs {away_team} at {event['startTimestamp']}.json"
                                cleaned_event = events.clean_pre_event(event)
                                odds = events.get_odds(event["id"])
                                cleaned_event["odds"] = odds
                                persist(
                                    collection="events",
                                    mongo_doc={
                                        "_id": event["id"],
                                        "home_team": home_team,
                                        "away_team": away_team,
                                        "startTimestamp": event["startTimestamp"],
                                        "event_data": cleaned_event,
                                    },
                                    json_path=output_filename,
                                    json_data=cleaned_event,
                                    filter_fields=["_id"],
                                )

                    except Exception as e:
                        # Some requests (such as 204 or pending responses) have no content and will error here.
                        # We safely ignore those.
                        logger.warning(f"⚠️ Could not retrieve response body for {url}: {e}")

    except Exception as e:
        logger.error(f"❌ A general error occurred: {e}")

    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.warning("⚠️ Error closing the browser: %s", e)

    for team in team_list:
        logger.info(f"📊 Fetching recent stats for {team.name}...")
        team.get_team_recent_performance(store=True)
        logger.info(f"📋 Fetching last matches for {team.name}...")
        team.get_team_last_matches(store=True)
        logger.info(f"👥 Fetching squad for {team.name}...")
        squad = team.get_team_squad(store=True)
        team_seasons = team.get_team_seasons(store=True)
        for tournament_name, tournament_data in team_seasons.items():
            tournament_id = tournament_data["tournament_id"]
            for season in tournament_data["seasons"]:
                season_id = season["season_id"]
                season_year = season["season_year"]
                logger.info(f"📈 Fetching stats for {team.name} in {tournament_name} - {season['season_name']}...")
                team.get_team_stats(tournament_id, tournament_name, season_id, season['season_name'], season_year, store=True)
        for player in squad:
            logger.info(f"👤 Fetching stats for player {player.name}...")
            player_obj = players.Player(player.player_id, player.name)
            player_obj.get_player_total_stats(store=True)

    logger.info("✅ Extraction completed successfully.")


if __name__ == "__main__":
    run_extractor()

