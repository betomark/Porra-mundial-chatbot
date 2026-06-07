# Porra Mundial Chatbot

This project is a Python-based chatbot designed to interact with users about the World Cup. It leverages the Google Gemini AI for conversational capabilities, extracts real-time (or near real-time) World Cup data, and stores information in a MongoDB database. The "Porra" aspect suggests a betting pool or prediction game related to the World Cup.

## Features

*   **World Cup Data Extraction:** Gathers information about tournaments, teams, players, and scheduled events.
*   **Power Rankings:** Calculates and stores power rankings for leagues and teams.
*   **Google Gemini Integration:** Utilizes the Gemini AI model for natural language understanding and generation, enabling interactive conversations about World Cup data.
*   **MongoDB Persistence:** Stores extracted data and calculated rankings in a MongoDB database for efficient retrieval and management.
*   **Docker Support:** Provides `docker-compose.yml` for easy setup and deployment of the application and its dependencies (e.g., MongoDB).

## Project Structure

*   `docker-compose.yml`: Defines the services for Docker Compose (e.g., Python application, MongoDB).
*   `requirements.txt`: Lists all Python dependencies.
*   `events.py`: Manages World Cup events.
*   `gemini.py`: Handles interactions with the Google Gemini API.
*   `league_power_ranking.py`: Logic for calculating and managing league power rankings.
*   `players.py`: Manages player data.
*   `teams.py`: Manages team data.
*   `tournaments.py`: Manages tournament data.
*   `urls.py`: Potentially defines API endpoints or routes (if this is a web application).
*   `world_cup_extractor.py`: Script for extracting World Cup-related data from external sources.
*   `data/`: Directory for storing JSON data (e.g., scheduled events, power rankings, team data).
*   `utils/`: Contains utility scripts:
    *   `folder_maker.py`: Utility for creating folders.
    *   `hf_client.py`: Client for Hugging Face interactions (if applicable).
    *   `llm_client.py`: Generic client for Large Language Model interactions.
    *   `mongo_client.py`: Client for connecting to and interacting with MongoDB.

## Installation

### Prerequisites

*   Docker and Docker Compose (recommended for easy setup)
*   Python 3.8+
*   `pip` (Python package installer)

### Using Docker Compose (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Porra-mundial-chatbot.git
    cd Porra-mundial-chatbot
    ```
2.  **Set up environment variables:**
    Copy the `.env-template` file to `.env` and fill in your Google Gemini API key and any other necessary configurations.
    ```bash
    cp .env-template .env
    # Open .env and add your GOOGLE_API_KEY and other settings
    ```
3.  **Build and run the services:**
    ```bash
    docker-compose up --build
    ```
    This will start the Python application and a MongoDB instance.

### Manual Installation (Without Docker)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Porra-mundial-chatbot.git
    cd Porra-mundial-chatbot
    ```
2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```
3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Set up environment variables:**
    Copy the `.env-template` file to `.env` and fill in your Google Gemini API key and any other necessary configurations.
    ```bash
    cp .env-template .env
    # Open .env and add your GOOGLE_API_KEY and other settings
    ```
6.  **Start MongoDB:**
    You will need a running MongoDB instance. You can install it locally or run it via Docker separately:
    ```bash
    docker run -d -p 27017:27017 --name mongo mongo:latest
    ```

## Usage

(Further instructions on how to run the chatbot or specific scripts will go here.)
For example:
```bash
python main.py
```

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

## License

This project is under GNU GENERAL PUBLIC LICENSE Version 3
