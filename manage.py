from flask_script import Manager
from python_search.frontend.app import app
from python_search import scraper

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


@manager.command
def run():
    app.run()


if __name__ == "__main__":
    manager.run()
