# AI News Recommender

AI News Recommender is a small Python web app that fetches English news from NewsAPI and presents it through a Gradio interface. Groq generates short summaries and suggested categories, while a local JSON file records reading categories so the app can recommend articles from categories the user has recently read. It is intended as a straightforward demonstration of news APIs, LLM-assisted processing, and a lightweight user interface.

## Features

- Browse NewsAPI top headlines by category and choose the number of articles.
- Generate short summaries and suggested categories with Groq.
- Get recommendations based on categories in the recent local reading history; defaults to technology, business, and science when there is no recent history.
- Store reading history in a local `user_prefs_default.json` file.
- Run locally or in Docker.

## Tech stack

- Python 3.11+
- Gradio
- NewsAPI (`newsapi-python`)
- Groq Python SDK
- `python-dotenv`
- Docker

## Architecture and flow

1. `main.py` builds the Gradio interface and handles user actions.
2. `agent.py` calls NewsAPI for headlines, then sends article descriptions and metadata to Groq for summaries and category suggestions.
3. Recommendation requests read the local preference JSON file, select up to three recently read categories, and fetch two headlines per category.
4. The UI renders the processed article results and links to the original publisher.

## Setup

Use Python 3.11 or newer.

```bash
git clone <repository-url>
cd ai-news-recommender
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Set the API credentials in `.env`, then start the app:

```bash
python main.py
```

Open `http://localhost:7861` by default.

## Environment variables

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `GROQ_API_KEY` | Yes | — | Groq API credential for summaries and categorization. |
| `NEWS_API_KEY` | Yes | — | NewsAPI credential for headlines. |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq chat model used for both tasks. |
| `HOST` | No | `0.0.0.0` | Gradio bind address. |
| `PORT` | No | `7861` | Gradio listening port. |

Keep real credentials in `.env` or your deployment secret manager; do not commit them.

## Docker

Build and run with a local `.env` file:

```bash
docker build -t ai-news-recommender .
docker run --rm --env-file .env -p 7861:7861 ai-news-recommender
```

The container binds to `0.0.0.0` and listens on port `7861` by default. To use another port, set `PORT` in the container and map the same container port, for example `-e PORT=8080 -p 8080:8080`.

## Known limitations

- News retrieval depends on NewsAPI availability, account limits, and its plan restrictions.
- Summaries and category suggestions depend on Groq availability and can fail or vary between calls.
- Reading history is local to the process filesystem and uses one default profile; it is not a multi-user or durable hosted database.
- The recommendation logic uses recent category frequency and does not learn from clicks or rank article quality.
- Results use article descriptions supplied by NewsAPI; the app does not retrieve full publisher article text.

## Future improvements

- Add explicit per-user profiles and durable storage.
- Add caching, request-level status feedback, and configurable timeouts.
- Add pagination and more flexible search and filtering.
- Add automated coverage for API failures and recommendation behavior.

## Screenshots

Screenshots are not included yet. Add application screenshots here when available, for example:

- `docs/screenshots/home.png` — main news browsing screen
- `docs/screenshots/recommendations.png` — recommendation results
