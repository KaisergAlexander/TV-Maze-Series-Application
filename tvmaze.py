"""Shared TVmaze API logic, used by both main.py (terminal) and app.py (web)."""

import requests

BASE_URL = "https://api.tvmaze.com"
TIMEOUT = 10  # seconds


class TVmazeError(Exception):
    """Raised with a user-friendly message when an API call fails."""


def get_json(endpoint, params=None):
    """Call a TVmaze endpoint and return the parsed JSON."""
    try:
        response = requests.get(BASE_URL + endpoint, params=params, timeout=TIMEOUT)
        response.raise_for_status()  # raises an error for 4xx / 5xx codes
        return response.json()
    except requests.exceptions.HTTPError as err:
        raise TVmazeError(f"The server answered with an error: {err}")
    except requests.exceptions.ConnectionError:
        raise TVmazeError("Could not connect. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise TVmazeError("The request timed out. Try again later.")
    except requests.exceptions.RequestException as err:
        raise TVmazeError(f"Something went wrong: {err}")
    except ValueError:
        raise TVmazeError("The response was not valid JSON.")


def search_show(name):
    """Endpoint 1: GET /search/shows?q=<name>. Returns the best match, or None."""
    results = get_json("/search/shows", params={"q": name})
    if not results:
        return None
    # Results are sorted by relevance, so the first one is the best match.
    return results[0]["show"]


def get_episodes(show_id):
    """Endpoint 2: GET /shows/<id>/episodes. Returns a list of episodes."""
    return get_json(f"/shows/{show_id}/episodes")


def group_by_season(episodes):
    """Turn a flat episode list into {season_number: [episodes]}, sorted by season."""
    seasons = {}
    for episode in episodes:
        seasons.setdefault(episode["season"], []).append(episode)
    return dict(sorted(seasons.items()))
