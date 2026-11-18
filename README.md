# TV Maze Series Application

A small Python app that teaches how REST APIs work, using the free [TVmaze API](https://www.tvmaze.com/api). Enter a TV show name and see all its episodes grouped by season. It works in the browser (Flask, `http://localhost:5000`) or in the terminal.

## What is implemented so far

- Local web interface (Flask) with a search box, at `http://localhost:5000`
- Terminal version (`main.py`) using `input()`
- Show search via the TVmaze API, then episode retrieval using the show ID from the search
- Episodes grouped by season with episode numbers and titles
- A box showing which API endpoints were called and why
- Error handling: empty input, show not found, no connection, timeout, HTTP errors, invalid JSON
- Shared API code in `tvmaze.py`, used by both interfaces

## Project structure

| File | Purpose |
|---|---|
| `tvmaze.py` | All TVmaze API logic (`search_show`, `get_episodes`, `group_by_season`, error handling) |
| `app.py` | Flask web app (one route, `/`) |
| `templates/index.html` | The HTML page (search form, endpoints box, episodes) |
| `static/style.css` | Basic CSS |
| `main.py` | Terminal version |
| `requirements.txt` | Dependencies: `requests`, `flask` |

## How it works (step by step)

1. You type a show name in the search box and press **Search**. The browser requests `/?q=<name>` from the Flask app.
2. Empty input is rejected with a message.
3. `app.py` calls `search_show()`, which sends `GET /search/shows?q=<name>` to TVmaze. The response is a list of matches sorted by relevance.
4. The first match is used and its `id` is read.
5. `app.py` calls `get_episodes(id)`, which sends `GET /shows/<id>/episodes`.
6. `group_by_season()` groups the episodes by their `season` field.
7. The template shows the endpoints used, then each season with its episode numbers and titles. Specials without an episode number are labelled "Special".

If any API call fails, `tvmaze.py` raises a `TVmazeError` with a friendly message and the page shows it instead of crashing.

## API endpoints used

Base URL: `https://api.tvmaze.com`

| Endpoint | Why we need it |
|---|---|
| `GET /search/shows?q=<name>` | Turns a name typed by a human into a show object, including its unique numeric `id`. |
| `GET /shows/<id>/episodes` | Returns every episode of one show (season, number, title, ...). |

### How the show ID connects the two requests

The episodes endpoint cannot take a name, only an ID. The first request returns `{"show": {"id": 66, "name": "The Big Bang Theory", ...}}`. The app reads `show["id"]` (66) and puts it into the URL of the second request: `/shows/66/episodes`. The output of request 1 is the input of request 2.

## Installation and execution

Requires Python 3. From the project folder (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the web interface and open <http://localhost:5000>:

```powershell
python app.py
```

Or run the terminal version:

```powershell
python main.py
```

Stop the web server with `Ctrl+C`.

### VS Code: "Import requests could not be resolved"

This warning means VS Code is using a different Python than the one where the packages are installed. Fix:

1. Create the virtual environment and install the requirements (above).
2. Press `Ctrl+Shift+P` -> **Python: Select Interpreter**.
3. Choose `.venv` (`.\.venv\Scripts\python.exe`). If it is not listed, choose **Enter interpreter path...** and browse to that file.
4. If the warning remains, run **Developer: Reload Window**.

## Example

Open <http://localhost:5000>, type `The Big Bang Theory` and click Search. The page shows:

```
API endpoints used
1. GET /search/shows?q=The Big Bang Theory - Turns the name you typed into a show, including its unique ID.
2. GET /shows/66/episodes - Uses the ID 66 from the first call to load all episodes.

The Big Bang Theory (ID 66, 279 episodes)

Season 1 (17 episodes)
  Episode 1: Pilot
  Episode 2: The Big Bran Hypothesis
  ...
```

Searching for a name that does not exist (e.g. `xqzzyxqwv`) shows: `No show found for 'xqzzyxqwv'. Try another name.`

## Possible future features

- Let the user pick from several search matches instead of the first one
- Show details (rating, genres, summary, poster) from `GET /shows/<id>`
- Show cast via `GET /shows/<id>/cast`
- Episode air dates and per-season statistics

## Development Progress

| Version | What was added |
|---|---|
| v0.1 | Terminal app: `/search/shows` and `/shows/{id}/episodes`, season grouping, endpoint explanation, error handling. |
| v0.2 | Fixed the VS Code `requests` import warning (project `.venv`, interpreter instructions). Moved API logic into `tvmaze.py`. Added Flask web interface at `localhost:5000` (HTML + CSS, no JavaScript). Added `flask` to `requirements.txt`. |

> Maintenance rule: update this README (features, endpoints, progress table) whenever functionality is added.
