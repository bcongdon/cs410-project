from flask import Flask, render_template, request
from ..scraper.model import Message
from ..indexer.indexer import IndexSearcher
from markdown import markdown
from .render import render_as_html

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get('query')
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = [list(result) for result in searcher.search(query)]

    for result in search_results:
        result[2] = render_as_html(result[2])

    return render_template(
        "index.html", search_results=search_results
    )


@app.route("/thread/<thread_id>")
def get_list(thread_id):
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = list(searcher.search_for_thread(thread_id))
    search_results.sort(key=lambda tup: tup[-1])

    return render_template(
        "index.html", search_results=search_results,
        hide_thread=True
    )


if __name__ == "__main__":
    app.run(debug=True)
