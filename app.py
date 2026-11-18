"""Flask web interface for the TVmaze Series Explorer. Run: python app.py"""

from flask import Flask, render_template, request

import tvmaze
from tvmaze import TVmazeError

app = Flask(__name__)


def error_page(message, status=500):
    return render_template("error.html", message=message), status


@app.route("/")
def home():
    try:
        shows = tvmaze.get_top_rated()
    except TVmazeError:
        shows = []  # the home page still works without the show list
    return render_template("home.html", shows=shows)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    kind = request.args.get("type", "show")
    if kind not in ("show", "actor"):
        kind = "show"
    if not query:
        return error_page("Please enter a name to search for.", 400)

    try:
        if kind == "show":
            return render_template("search.html", query=query, kind=kind,
                                   shows=tvmaze.search_shows(query))
        people = tvmaze.search_people(query)[:12]
        # Load the credits of the best 3 matches; the others link to their own page.
        credits = {p["id"]: tvmaze.get_credits(p["id"])[:6] for p in people[:3]}
        return render_template("search.html", query=query, kind=kind,
                               people=people, credits=credits)
    except TVmazeError as err:
        return error_page(f"API error: {err}", 502)


@app.route("/show/<int:show_id>")
def show_detail(show_id):
    try:
        show = tvmaze.get_show(show_id)
        episodes = tvmaze.get_episodes(show_id)
    except TVmazeError as err:
        return error_page(f"API error: {err}", 404 if "not found" in str(err) else 502)

    # Cast and recommendations are extras: if they fail, the page still works.
    try:
        cast = tvmaze.get_cast(show_id)
    except TVmazeError:
        cast = []
    try:
        related = tvmaze.get_related_shows(show)
    except TVmazeError:
        related = []

    return render_template(
        "show.html", show=show, cast=cast, related=related,
        summary=tvmaze.strip_html(show.get("summary")),
        seasons=tvmaze.group_by_season(episodes), total=len(episodes))


@app.route("/person/<int:person_id>")
def person_detail(person_id):
    try:
        person = tvmaze.get_person(person_id)
        shows = tvmaze.get_credits(person_id)
    except TVmazeError as err:
        return error_page(f"API error: {err}", 404 if "not found" in str(err) else 502)
    return render_template("person.html", person=person, shows=shows)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
