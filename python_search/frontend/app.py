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

	#search_results = [Message(text="Hello world")]
	return render_template(
		"index.html", search_results=search_results
	)


if __name__ == "__main__":
	app.run(debug=True)
