# Octopus Project

Octopus is a modular scraping and automation framework designed to manage multiple independent workers, referred to as **Tentacles**. Each tentacle is a specialized process responsible for interacting with a specific target website or service.

## Architecture

The project follows a modular inheritance-based design:

### Core Components
- **`BaseTentacle`**: The abstract base class located in `tentacles/base_tentacle.py`. It provides essential boilerplate for all tentacles, including:
    - **Task Management**: Uses `asyncio` to run tentacles concurrently within a single event loop.
    - **Logging**: Integrated logging for tracking activity and errors.
    - **State Management**: Methods to save and load JSON state to maintain continuity between runs.
    - **Status Tracking**: Standardized status reporting (e.g., "Running", "Stopped", "Error").

### User Interface
- **TUI Dashboard**: A terminal-based interface built with `urwid` for monitoring and controlling all tentacles in real-time.

### Implementation (Tentacles)
- **`QuotesTentacle`**: A scraper designed for `quotes.toscrape.com`, demonstrating how to handle pagination and simple HTML parsing.
- **`DummyTentacle`**: A boilerplate implementation used for testing the lifecycle of a process without performing external requests.

## Configuration & Security

The project uses environment variables for sensitive data. 
- **Root `.env`**: Stores global credentials used across all tentacles.
- **Local `.env`**: Each tentacle directory can optionally contain its own `.env` for overrides or site-specific configurations.

## Development

### Prerequisites
- Python 3.x
- `beautifulsoup4`: For HTML parsing.
- `python-dotenv`: For environment variable management.
- `httpx`: For asynchronous HTTP requests.
- `urwid`: For the lightweight TUI interface.
- `pytest-asyncio`: For running asynchronous tests.

### Environment Setup
It is highly recommended to use a Python virtual environment to manage dependencies:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running a Tentacle
Tentacles should be executed as modules from the project root to ensure imports are resolved correctly:
```bash
python -m tentacles.quotes_tentacle.quotes_tentacle
```

### Testing
The project uses `pytest` for unit and integration testing. Tests are located in the `tests/` directory and utilize `unittest.mock` to isolate tentacles from real network calls.

To run the full test suite:
```bash
pytest
```

## Roadmap
- Implement a persistence layer (e.g., SQLite) for scraped data.
- Add a web UI to complement the existing TUI dashboard.