# Porra Mundial Chatbot

This project is a Python-based chatbot designed to interact with users about the World Cup. It leverages the Google Gemini AI for conversational capabilities, extracts real-time (or near real-time) World Cup data, and stores information in a MongoDB database. The "Porra" aspect suggests a betting pool or prediction game related to the World Cup.

## Features

* **World Cup Data Extraction:** Gathers information about tournaments, teams, players, and scheduled events.
* **Power Rankings:** Calculates and stores power rankings for leagues and teams.
* **Google Gemini Integration:** Utilizes the Gemini AI model for natural language understanding and generation, enabling interactive conversations about World Cup data.
* **MongoDB Persistence:** Stores extracted data and calculated rankings in a MongoDB database for efficient retrieval and management.
* **Docker Support:** Provides `docker-compose.yml` for easy setup and deployment of the application and its dependencies (e.g., MongoDB).

## Project Structure

* `docker-compose.yml`: Defines the services for Docker Compose (e.g., Python application, MongoDB).
* `requirements.txt`: Lists the core runtime dependencies for the application.
* `main.py`: Entry point for running extraction and prediction workflows.
* `porra/`: Main application package containing the core domain logic:
  * `events.py`: Manages World Cup events.
  * `gemini.py`: Handles interactions with the Google Gemini API.
  * `league_power_ranking.py`: Logic for calculating and managing league power rankings.
  * `players.py`: Manages player data.
  * `teams.py`: Manages team data.
  * `tournaments.py`: Manages tournament data.
  * `urls.py`: SofaScore API endpoint definitions.
  * `world_cup_extractor.py`: Script for extracting World Cup-related data from external sources.
* `data/`: Directory for storing JSON data (e.g., scheduled events, power rankings, team data).
* `utils/`: Contains utility scripts:
  * `folder_maker.py`: Utility for creating folders.
  * `hf_client.py`: Client for Hugging Face interactions (if applicable).
  * `llm_client.py`: Generic client for Large Language Model interactions.
  * `mongo_client.py`: Client for connecting to and interacting with MongoDB.

## Installation

### Prerequisites

* Docker and Docker Compose (recommended for easy setup)
* Python 3.8+
* `pip` (Python package installer)

### Using Docker Compose (Recommended)

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Porra-mundial-chatbot.git
    cd Porra-mundial-chatbot
    ```

2. **Set up environment variables:**
    Copy the `.env-template` file to `.env` and fill in your Google Gemini API key and any other necessary configurations.

    ```bash
    cp .env-template .env
    # Open .env and add your GEMINI_API_KEY and other settings
    ```

3. **Build and run the services:**

    ```bash
    docker compose up --build
    ```

    This will start MongoDB and build the Python app container. The default app command runs the World Cup extraction workflow in headless mode and will stop once the extraction finishes.

4. **Run containerized tasks manually:**

    ```bash
    docker compose run --rm app python main.py extract --headless
    docker compose run --rm app python main.py predict <event_id> <team_a_id> <team_b_id>
    docker compose run --rm app python main.py show-collections
    ```

## API Service

Once the Docker Compose stack is running, the API is available at `http://localhost:8000`.

### Endpoints

* `GET /health` — checks app and Mongo connectivity.
* `GET /collections` — lists MongoDB collections.
* `GET /documents` — retrieves documents from a MongoDB collection with optional field filtering.
* `POST /extract` — queues a background extraction task.
* `POST /predict` — generates a prediction from Gemini.

### Example API requests

```bash
curl http://localhost:8000/health
curl http://localhost:8000/collections
curl "http://localhost:8000/documents?collection=events&field=country&value=Brazil&limit=20"
curl -X POST http://localhost:8000/extract -H "Content-Type: application/json" -d '{"headless": true}'
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"event_id":"12345","team_a_id":"1","team_b_id":"2"}'
```

### Manual Installation (Without Docker)

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Porra-mundial-chatbot.git
    cd Porra-mundial-chatbot
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv .venv
    ```

3. **Activate the virtual environment:**
    * **Windows:**

        ```bash
        .venv\Scripts\activate
        ```

    * **macOS/Linux:**

        ```bash
        source .venv/bin/activate
        ```

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment variables:**
    Copy the `.env-template` file to `.env` and fill in your Google Gemini API key and any other necessary configurations.

    ```bash
    cp .env-template .env
    # Open .env and add your GOOGLE_API_KEY and other settings
    ```

6. **Start MongoDB:**
    You will need a running MongoDB instance. You can install it locally or run it via Docker separately:

    ```bash
    docker run -d -p 27017:27017 --name mongo mongo:latest
    ```

## Usage

Use the `main.py` entry point for the extractor and prediction workflows.

Examples:

```bash
python main.py extract --headless
python main.py predict <event_id> <team_a_id> <team_b_id>
python main.py show-collections
```

If you are using Docker Compose, run:

```bash
docker compose run --rm app python main.py extract --headless
```

> Note: The main application logic now lives under the `porra/` package, so imports and execution paths are organized for better maintainability.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## License

This project is under GNU GENERAL PUBLIC LICENSE Version 3
