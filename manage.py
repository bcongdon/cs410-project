from flask_script import Manager
from python_search.frontend.app import app
from python_search import scraper

manager = Manager(app)


@manager.command
def scrape():
    scraper.scrape_cmd()


@manager.command
def run():
    app.run()

if __name__ == '__main__':
    manager.run()
