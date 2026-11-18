"""Shared TVmaze API logic, used by both main.py (terminal) and app.py (web)."""

import re
from functools import lru_cache

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
        if err.response is not None and err.response.status_code == 404:
            raise TVmazeError("The requested item was not found.")
        raise TVmazeError(f"The server answered with an error: {err}")
    except requests.exceptions.ConnectionError:
        raise TVmazeError("Could not connect. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise TVmazeError("The request timed out. Try again later.")
    except requests.exceptions.RequestException as err:
        raise TVmazeError(f"Something went wrong: {err}")
    except ValueError:
        raise TVmazeError("The response was not valid JSON.")


# ---------- Shows ----------

def search_shows(name):
    """GET /search/shows?q=<name>. Returns a list of shows, best match first."""
    results = get_json("/search/shows", params={"q": name})
    return [item["show"] for item in results]


def search_show(name):
    """Return only the best matching show (or None). Used by the terminal app."""
    shows = search_shows(name)
    return shows[0] if shows else None


@lru_cache(maxsize=128)
def get_show(show_id):
    """GET /shows/<id>. Returns the full details of one show."""
    return get_json(f"/shows/{show_id}")


@lru_cache(maxsize=128)
def get_episodes(show_id):
    """GET /shows/<id>/episodes. Returns a list of episodes."""
    return get_json(f"/shows/{show_id}/episodes")


def group_by_season(episodes):
    """Turn a flat episode list into {season_number: [episodes]}, sorted by season."""
    seasons = {}
    for episode in episodes:
        seasons.setdefault(episode["season"], []).append(episode)
    return dict(sorted(seasons.items()))


@lru_cache(maxsize=128)
def get_cast(show_id, limit=12):
    """GET /shows/<id>/cast. Returns the first `limit` different actors."""
    cast, seen = [], set()
    for entry in get_json(f"/shows/{show_id}/cast"):
        person_id = entry["person"]["id"]
        if person_id not in seen:  # an actor can appear twice (two characters)
            seen.add(person_id)
            cast.append(entry)
    return cast[:limit]


# ---------- People ----------

def search_people(name):
    """GET /search/people?q=<name>. Returns a list of people, best match first."""
    results = get_json("/search/people", params={"q": name})
    return [item["person"] for item in results]


@lru_cache(maxsize=128)
def get_person(person_id):
    """GET /people/<id>. Returns the details of one person."""
    return get_json(f"/people/{person_id}")


@lru_cache(maxsize=128)
def get_credits(person_id):
    """GET /people/<id>/castcredits?embed=show. Returns the shows a person acted in."""
    credits = get_json(f"/people/{person_id}/castcredits", params={"embed": "show"})
    shows, seen = [], set()
    for credit in credits:
        show = credit["_embedded"]["show"]
        if show["id"] not in seen:  # remove duplicates (several roles in one show)
            seen.add(show["id"])
            shows.append(show)
    # Newest shows first; shows without a premiere date go last.
    shows.sort(key=lambda s: s.get("premiered") or "", reverse=True)
    return shows


# ---------- Related shows ----------

@lru_cache(maxsize=16)
def get_shows_page(page):
    """GET /shows?page=<n>. Returns one page of 250 shows (not the whole catalogue)."""
    return get_json("/shows", params={"page": page})


def get_related_shows(show, limit=6):
    """Recommend shows that share genres with `show`.

    To stay efficient we download only ONE page of the show index (the page that
    contains this show, 250 shows) instead of the whole catalogue. Shows are
    ranked by number of shared genres, then by TVmaze rating.
    """
    genres = set(show.get("genres") or [])
    if not genres:
        return []
    candidates = []
    for other in get_shows_page(show["id"] // 250):
        shared = genres & set(other.get("genres") or [])
        if other["id"] != show["id"] and shared:
            rating = (other.get("rating") or {}).get("average") or 0
            candidates.append((len(shared), rating, sorted(shared), other))
    candidates.sort(key=lambda c: (c[0], c[1]), reverse=True)
    return [dict(other, shared_genres=shared) for _, _, shared, other in candidates[:limit]]


def get_top_rated(limit=12):
    """Highest rated shows of the first index page, for the home page."""
    rated = [s for s in get_shows_page(0) if (s.get("rating") or {}).get("average")]
    rated.sort(key=lambda s: s["rating"]["average"], reverse=True)
    return rated[:limit]


# ---------- Helpers for display ----------

def strip_html(text):
    """TVmaze summaries contain HTML tags such as <p> and <b>; remove them."""
    return re.sub(r"<[^>]+>", "", text or "").strip()
