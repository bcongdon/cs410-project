from flask_script import Manager
from python_search.frontend.app import app
from python_search import scraper, indexer

manager = Manager(app)


@manager.option(
    "--parallelism",
    help="The number of parallel scraping processes to use",
    type=int,
    default=1,
)
@manager.option(
    "--start_at", help="The mailing list to start at (alphabetically)"
)
@manager.option("--update", type=bool)
def scrape(parallelism, start_at, update):
    scraper.scrape_cmd(parallelism, start_at, update)


@manager.option(
    "--db",
    help="The file of the database",
    required=True
)
@manager.option(
    "--index_dir", help="The directory of the index",
    required=True
)
def index(db, index_dir):
    indexer.index_cmd(db, index_dir)


@manager.option(
    "--index_dir", help="The directory of the index",
    required=True
)
@manager.option(
    "--query", help="Query to search index for",
    required=True
)
def search(index_dir, query):
    searcher = indexer.IndexSearcher(index_dir)
    results = searcher.search(query)
    print(list(results))


@manager.command
def run():
    app.run()


if __name__ == "__main__":
    manager.run()
