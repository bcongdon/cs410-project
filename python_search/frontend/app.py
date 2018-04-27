from flask import Flask, render_template, request
from dateutil.parser import parse 
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
    daterange = request.args.get('daterange', '')
    mail_list_id = request.args.get('mail-id', '')
    searcher = IndexSearcher(app.config["index_dir"])
    search_results = [result for result in searcher.search(query) 
                    if within_range(result.sent_at, daterange) and same_list(result.list_id, mail_list_id)]
    
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


def within_range(sent_time, daterange):
    if not daterange:
        return True
    date_parts = daterange.split('-')
    start_date = parse(date_parts[0].strip())
    end_date = parse(date_parts[1].strip())
    return sent_time >= start_date and sent_time < end_date


def same_list(result_list_id, filter_list_id):
    if not filter_list_id:
        return True
    return filter_list_id == result_list_id

if __name__ == "__main__":
    app.run(debug=True)
