# TV Maze Series Application

A TV show discovery website built with Flask and the free [TVmaze API](https://www.tvmaze.com/api). Search for shows or actors and see ratings, cast, episodes by season and similar shows, in a modern dark interface. It also teaches how REST APIs work: every feature below is built from real API responses.

## Features

- **Dark, responsive UI** (IMDb/Netflix style): sticky navigation with search bar, poster cards with hover effects, works on phones.
- **Home page** with the top rated shows.
- **Show search**: results as poster cards with rating and year.
- **Show page**: poster, genres, status, runtime, network, description.
- **Ratings**: the TVmaze rating (`rating.average`) is shown prominently. TVmaze does not provide IMDb scores, only IMDb IDs, so the page shows a link to the show's IMDb page when an ID exists. Missing ratings show "Not available". No scraping, no other rating source, no API keys.
- **Cast**: main cast with actor photo, name and character. Each actor is clickable.
- **Actor pages**: an actor's other TV shows (newest first), each clickable.
- **Actor search**: choose "Actors" in the search bar to find actors and see their TV credits.
- **Episodes**: grouped by season in collapsible sections (`<details>`), with episode number, title and air date. Specials are labelled "Special".
- **You Might Also Like**: shows that share genres with the current show, with posters and ratings (see below).
- **Error handling**: empty search, nothing found, unknown show/person (404 page), connection errors, timeouts, HTTP errors, missing images (placeholder), missing ratings, missing cast. If cast or recommendations fail, the rest of the page still loads.
- **Terminal version** (`main.py`) that still prints episodes by season.

## Technologies

Python 3, [Flask](https://flask.palletsprojects.com/), [requests](https://requests.readthedocs.io/), HTML (Jinja2 templates), CSS. No JavaScript is needed. No database. Responses are cached in memory with `functools.lru_cache` to avoid repeated calls.

## Project structure

| File | Purpose |
|---|---|
| `tvmaze.py` | All TVmaze API logic and error handling (shared by web and terminal) |
| `app.py` | Flask routes: `/`, `/search`, `/show/<id>`, `/person/<id>` |
| `templates/` | `base.html` (layout), `_macros.html` (cards), `home.html`, `search.html`, `show.html`, `person.html`, `error.html` |
| `static/style.css` | Dark theme and responsive layout |
| `main.py` | Terminal version |
| `requirements.txt` | Dependencies: `requests`, `flask` |

## API endpoints used

Base URL: `https://api.tvmaze.com`

| Endpoint | Why we need it |
|---|---|
| `GET /search/shows?q=<name>` | Turns a name typed by a human into a list of matching shows, each with a unique numeric `id`. |
| `GET /shows/<id>` | Full details of one show: poster, genres, `rating.average`, status, summary and `externals.imdb` (the IMDb ID used for the IMDb link). |
| `GET /shows/<id>/episodes` | Every episode of one show (season, number, title, air date). |
| `GET /shows/<id>/cast` | The actors of a show and the characters they play, including each actor's `person.id`. |
| `GET /search/people?q=<name>` | Turns an actor name into a list of matching people, each with a unique `id`. |
| `GET /people/<id>` | Details of one person (photo, birthday, country). |
| `GET /people/<id>/castcredits?embed=show` | The shows a person acted in. `embed=show` includes the full show data (poster, rating) in the same response, so no extra request per show is needed. |
| `GET /shows?page=<n>` | One page of 250 shows from the TVmaze index (genres and rating included). Used for the home page and for recommendations. |

### How IDs connect the requests

The endpoints cannot take names, only IDs, so one request provides the ID for the next one.

**Show ID**
1. `/search/shows?q=The Big Bang Theory` returns the show with `id` 66.
2. The app uses 66 in `/shows/66` (details), `/shows/66/episodes` (episodes) and `/shows/66/cast` (cast). The page URL is `/show/66` as well, so every show page is addressable by its ID.

**Person ID**
1. `/shows/66/cast` (or `/search/people?q=...`) returns each actor with a `person.id`, e.g. 4 for Johnny Galecki.
2. The app uses it in `/people/4` and `/people/4/castcredits?embed=show` to list the actor's other shows.
3. Each of those shows has its own `id`, which leads back to a show page. Shows and people link into each other this way.

### How "You Might Also Like" works

TVmaze has no "similar shows" endpoint, so recommendations are based on **genre similarity**:

1. Read the `genres` of the current show (from `/shows/<id>`).
2. Download one index page, `/shows?page=<id // 250>`, which is the page of 250 shows containing the current show. The whole catalogue (tens of thousands of shows) is never downloaded.
3. Keep the shows that share at least one genre, excluding the current show itself.
4. Rank them by number of shared genres, then by TVmaze rating, and show the best 6. The shared genres are shown on each card.

Because only one page is used, recommendations come from shows with nearby IDs (roughly the same period of TVmaze's catalogue). This is a deliberate trade-off for speed.

## Installation and execution

Requires Python 3. From the project folder (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000> in your browser. Stop the server with `Ctrl+C`.

Terminal version: `python main.py`

### VS Code: "Import requests could not be resolved"

VS Code is using a different Python than the one with the packages. Press `Ctrl+Shift+P` -> **Python: Select Interpreter** -> choose `.\.venv\Scripts\python.exe`, then run **Developer: Reload Window** if needed. The project's `.vscode/settings.json` already points to `.venv`.

## Development Progress

| Version | What was added |
|---|---|
| v0.1 | Terminal app: `/search/shows` and `/shows/{id}/episodes`, season grouping, error handling. |
| v0.2 | Fixed the VS Code `requests` import warning (project `.venv`). Moved API logic into `tvmaze.py`. First Flask web interface at `localhost:5000`. |
| v0.3 | Modern dark UI with posters and responsive cards. Show details and ratings (TVmaze rating, IMDb link). Cast with actor photos and clickable actors. Actor pages and actor search (`/search/people`, `/people/{id}/castcredits`). Collapsible episodes per season. "You Might Also Like" recommendations by genre. Removed API explanations from the website (documented here instead). Response caching. |

> Maintenance rule: update this README (features, endpoints, progress table) whenever functionality is added.
