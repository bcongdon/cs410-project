from flask import Flask, render_template, request
from ..scraper.model import Message
from ..indexer.indexer import IndexSearcher

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = list(searcher.search(query))

    return render_template(
        "index.html", search_results=search_results
    )


@app.route("/thread/<thread_id>")
def get_list(thread_id):
	searcher = IndexSearcher(app.config["index_dir"])
	search_results = list(searcher.search_for_thread(thread_id))
	search_results.sort(key = lambda tup: tup[5])

	return render_template(
        "index.html", search_results=search_results,
        hide_thread=True
    )

if __name__ == "__main__":
    app.run(debug=True)
