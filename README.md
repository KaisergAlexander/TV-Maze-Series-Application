# TV Maze Series Application

A small Python terminal app that teaches how REST APIs work, using the free [TVmaze API](https://www.tvmaze.com/api). You type a TV show name and the app prints all its episodes grouped by season.

## What is implemented so far

- Interactive prompt (`input()`) for a TV show name
- Show search via the TVmaze API
- Episode list retrieval using the show ID found in the search
- Episodes printed grouped by season, with episode numbers and titles
- Output showing which API endpoints were called and why
- Error handling: empty input, show not found, no connection, timeout, HTTP errors, invalid JSON

## How it works (step by step)

1. `python main.py` asks: `Enter a TV show name:`.
2. Empty input is rejected with a message.
3. The app sends `GET /search/shows?q=<name>`. The response is a list of matches sorted by relevance.
4. The app takes the first match and reads its `id`.
5. The app sends `GET /shows/<id>/episodes` with that ID.
6. The episodes are grouped by their `season` field and printed with their `number` and `name`.
7. A summary lists the endpoints that were called.

Every request goes through one helper, `get_json()`, which sets a timeout, checks the HTTP status and catches network errors, so all errors are handled in one place.

## API endpoints used

Base URL: `https://api.tvmaze.com`

| Endpoint | Why we need it |
|---|---|
| `GET /search/shows?q=<name>` | Turns a name typed by a human into a show object, including its unique numeric `id`. |
| `GET /shows/<id>/episodes` | Returns every episode of one show (season, number, title, ...). |

### How the show ID connects the two requests

The episodes endpoint cannot take a name, only an ID. The first request returns the show, e.g. `{"show": {"id": 66, "name": "The Big Bang Theory", ...}}`. The app reads `show["id"]` (66) and puts it into the URL of the second request: `/shows/66/episodes`. The output of request 1 is the input of request 2.

## Installation and execution

Requires Python 3.

```bash
pip install -r requirements.txt
python main.py
```

## Example

Input:

```
=== TVmaze Series Explorer ===
Enter a TV show name: The Big Bang Theory
```

Output (shortened):

```
Step 1: searching for the show
  [API] GET https://api.tvmaze.com/search/shows?q=The+Big+Bang+Theory  ->  200
  Found: The Big Bang Theory (2007), ID = 66

Step 2: fetching episodes for show ID 66
  [API] GET https://api.tvmaze.com/shows/66/episodes  ->  200

=== The Big Bang Theory: 279 episodes ===

Season 1 (17 episodes)
  Episode 1: Pilot
  Episode 2: The Big Bran Hypothesis
  ...

=== API endpoints used ===
1. GET /search/shows?q=The Big Bang Theory  - found the show and its ID (66)
2. GET /shows/66/episodes  - loaded the episode list
```

## Possible future features

- Let the user pick from several search matches instead of the first one
- Show show details (rating, genres, summary) from `GET /shows/<id>`
- Show cast via `GET /shows/<id>/cast`
- Episode air dates and per-season statistics
- Search again without restarting the program

## Development Progress

| Version | What was added |
|---|---|
| v0.1 | `main.py` with interactive input, `/search/shows` and `/shows/{id}/episodes` calls, season grouping, endpoint explanation output, error handling. `requirements.txt` and this README. |

> Maintenance rule: update this README (features, endpoints, progress table) whenever functionality is added.
