"""TVmaze Series Explorer - a beginner-friendly demo of a REST API.

Flow:
  1. Ask the user for a show name.
  2. GET /search/shows?q=<name>   -> find the show and its ID.
  3. GET /shows/<id>/episodes     -> get every episode of that show.
  4. Print the episodes grouped by season.
"""

import requests

BASE_URL = "https://api.tvmaze.com"
TIMEOUT = 10  # seconds


def get_json(endpoint, params=None):
    """Call a TVmaze endpoint and return the parsed JSON.

    Returns None (after printing a message) if something goes wrong.
    """
    url = BASE_URL + endpoint
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()  # raises an error for 4xx / 5xx codes
        print(f"  [API] GET {response.url}  ->  {response.status_code}")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"  [API ERROR] The server answered with an error: {err}")
    except requests.exceptions.ConnectionError:
        print("  [API ERROR] Could not connect. Check your internet connection.")
    except requests.exceptions.Timeout:
        print("  [API ERROR] The request timed out. Try again later.")
    except requests.exceptions.RequestException as err:
        print(f"  [API ERROR] Something went wrong: {err}")
    except ValueError:
        print("  [API ERROR] The response was not valid JSON.")
    return None


def search_show(name):
    """Endpoint 1: search shows by name. Returns the best match or None."""
    print("\nStep 1: searching for the show")
    print("  Why: the episodes endpoint needs a show ID, and search is how we get it.")
    results = get_json("/search/shows", params={"q": name})
    if results is None:
        return None
    if not results:
        print(f"  No show found for '{name}'.")
        return None
    # Results are sorted by relevance, so the first one is the best match.
    return results[0]["show"]


def get_episodes(show_id):
    """Endpoint 2: get all episodes of a show using its ID."""
    print(f"\nStep 2: fetching episodes for show ID {show_id}")
    print("  Why: this endpoint returns the full episode list of one show.")
    return get_json(f"/shows/{show_id}/episodes")


def group_by_season(episodes):
    """Turn a flat episode list into {season_number: [episodes]}."""
    seasons = {}
    for episode in episodes:
        seasons.setdefault(episode["season"], []).append(episode)
    return seasons


def print_episodes(episodes):
    seasons = group_by_season(episodes)
    for season_number in sorted(seasons):
        season_episodes = seasons[season_number]
        print(f"\nSeason {season_number} ({len(season_episodes)} episodes)")
        for ep in season_episodes:
            # Specials have no episode number, so we show "Special" instead.
            number = ep["number"] if ep["number"] is not None else "Special"
            print(f"  Episode {number}: {ep['name']}")


def main():
    print("=== TVmaze Series Explorer ===")
    name = input("Enter a TV show name: ").strip()
    if not name:
        print("You did not enter anything. Please run the program again.")
        return

    show = search_show(name)
    if show is None:
        return

    year = (show.get("premiered") or "unknown")[:4]
    print(f"  Found: {show['name']} ({year}), ID = {show['id']}")

    episodes = get_episodes(show["id"])
    if episodes is None:
        return
    if not episodes:
        print("  This show has no episodes listed.")
        return

    print(f"\n=== {show['name']}: {len(episodes)} episodes ===")
    print_episodes(episodes)

    print("\n=== API endpoints used ===")
    print(f"1. GET /search/shows?q={name}  - found the show and its ID ({show['id']})")
    print(f"2. GET /shows/{show['id']}/episodes  - loaded the episode list")


if __name__ == "__main__":
    main()
