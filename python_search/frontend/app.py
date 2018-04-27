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
    query = request.args.get('query', '')
    date_range = request.args.get('daterange', '')
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = [result for result in searcher.search(query)]

    for result in search_results:
        result.text = render_as_html(result.text)

    return render_template(
        "results.html", search_results=search_results, query=query
    )


@app.route("/thread/<thread_id>")
def get_list(thread_id):
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = list(searcher.search_for_thread(thread_id))
    search_results.sort(key=lambda res: res.thread_idx)

    for result in search_results:
        result.text = render_as_html(result.text)

    return render_template(
        "results.html",
        search_results=search_results,
        hide_thread=True,
        thread_id=thread_id,
    )


@app.route('/similar/<list_id>/<message_id>')
def get_similar(list_id, message_id):
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = list(searcher.find_similar_messages(list_id, message_id))

    for result in search_results:
        result.text = render_as_html(result.text)

    return render_template(
        "results.html",
        search_results=search_results,
    )


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
