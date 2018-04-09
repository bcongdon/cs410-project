from flask import Flask, render_template
from ..scraper.model import Message
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    search_results = [Message(message="Hello world")]
    return render_template('search_results.html',
                           search_results=search_results)


if __name__ == '__main__':
    app.run(debug=True)