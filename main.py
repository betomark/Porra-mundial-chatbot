import os
import argparse
import logging
from utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def run_extraction(headless=False):
    if headless:
        os.environ["HEADLESS"] = "true"
    from porra import world_cup_extractor
    world_cup_extractor.run_extractor()


def run_prediction(event_id, team_a_id, team_b_id, api_key=None, model=None):
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    if model:
        os.environ["GEMINI_MODEL"] = model

    from porra.gemini import gemini as Gemini
    predictor = Gemini()
    prediction = predictor.generate_prediction(event_id, team_a_id, team_b_id)
    print(prediction)


def list_collections():
    from utils.mongo_client import MongoDBClient
    client = MongoDBClient()
    collections = client.database.list_collection_names()
    logger.info("MongoDB collections: %s", collections)
    for name in collections:
        print(name)


def main():
    parser = argparse.ArgumentParser(
        description="Porra Mundial Chatbot CLI for extraction and prediction tasks."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="Run the World Cup data extractor.")
    extract_parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode.")

    predict_parser = subparsers.add_parser("predict", help="Generate a prediction for a match using Gemini.")
    predict_parser.add_argument("event_id", help="ID of the match/event.")
    predict_parser.add_argument("team_a_id", help="Identifier of team A.")
    predict_parser.add_argument("team_b_id", help="Identifier of team B.")
    predict_parser.add_argument("--api-key", help="Override GEMINI_API_KEY for this execution.")
    predict_parser.add_argument("--model", help="Override GEMINI_MODEL for this execution.")

    subparsers.add_parser("show-collections", help="List MongoDB collections available in the configured database.")

    args = parser.parse_args()

    if args.command == "extract":
        logger.info("Starting extraction flow (headless=%s).", args.headless)
        run_extraction(args.headless)
    elif args.command == "predict":
        logger.info("Starting prediction flow for event_id=%s", args.event_id)
        run_prediction(args.event_id, args.team_a_id, args.team_b_id, api_key=args.api_key, model=args.model)
    elif args.command == "show-collections":
        list_collections()
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
