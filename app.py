"""Flask web interface for the TVmaze Series Explorer. Run: python app.py"""

from flask import Flask, render_template, request

from tvmaze import TVmazeError, get_episodes, group_by_season, search_show

app = Flask(__name__)


@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    context = {"query": query, "show": None, "seasons": None,
               "total": 0, "error": None, "calls": []}

    if "q" in request.args and not query:
        context["error"] = "Please enter a TV show name."
    elif query:
        try:
            context["calls"].append({
                "endpoint": f"GET /search/shows?q={query}",
                "why": "Turns the name you typed into a show, including its unique ID.",
            })
            show = search_show(query)
            if show is None:
                context["error"] = f"No show found for '{query}'. Try another name."
            else:
                context["show"] = show
                context["calls"].append({
                    "endpoint": f"GET /shows/{show['id']}/episodes",
                    "why": f"Uses the ID {show['id']} from the first call to load all episodes.",
                })
                episodes = get_episodes(show["id"])
                context["total"] = len(episodes)
                context["seasons"] = group_by_season(episodes)
        except TVmazeError as err:
            context["error"] = f"API error: {err}"

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
