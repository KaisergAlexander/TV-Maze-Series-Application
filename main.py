"""Terminal version of the TVmaze Series Explorer (the web version is app.py)."""

from tvmaze import TVmazeError, get_episodes, group_by_season, search_show


def main():
    print("=== TVmaze Series Explorer ===")
    name = input("Enter a TV show name: ").strip()
    if not name:
        print("You did not enter anything. Please run the program again.")
        return

    try:
        print("\nStep 1: GET /search/shows?q=... (find the show and its ID)")
        show = search_show(name)
        if show is None:
            print(f"  No show found for '{name}'.")
            return
        print(f"  Found: {show['name']}, ID = {show['id']}")

        print(f"\nStep 2: GET /shows/{show['id']}/episodes (load all episodes)")
        episodes = get_episodes(show["id"])
    except TVmazeError as err:
        print(f"  [API ERROR] {err}")
        return

    if not episodes:
        print("  This show has no episodes listed.")
        return

    print(f"\n=== {show['name']}: {len(episodes)} episodes ===")
    for season, season_episodes in group_by_season(episodes).items():
        print(f"\nSeason {season} ({len(season_episodes)} episodes)")
        for ep in season_episodes:
            # Specials have no episode number, so we show "Special" instead.
            number = ep["number"] if ep["number"] is not None else "Special"
            print(f"  Episode {number}: {ep['name']}")


if __name__ == "__main__":
    main()
