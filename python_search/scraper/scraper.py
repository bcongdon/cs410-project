from bs4 import BeautifulSoup
import requests
from .mailing_list import MailingList
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import Base, Message
from multiprocessing import Pool
from datetime import datetime, timedelta
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
sys.setrecursionlimit(10000)


BLACKLISTED_LISTS = [
    "new-bugs-announce",
    "numpy-svn",
    "plpug",
    "pypy-commit",
    "pypy-issue",
    "pytest-issue",
    "python-checkins",
    "python-bugs-list",
    "pysilesia",
    "pytest-commit",
    "python-de",
    "python-es",
    "python-hu",
    "scipy-svn",
]


def get_list_ids():
    """
    Returns a list of all message lists (i.e. topics) from mail;
    """
    req = requests.get("https://mail.python.org/mailman/listinfo")
    soup = BeautifulSoup(req.text, "lxml")
    for row in soup.find("table").find_all("tr")[4:]:
        link = row.find("a", href=True)["href"]
        yield link.split("/")[-1]


def scrape_all(engine, start_at=None, parallelism=1, since=None):
    """
    Scrape all mailing lists on mail.python.org
    """
    session = sessionmaker(bind=engine)()

    for list_id in get_list_ids():
        if start_at is not None and list_id < start_at:
            continue

        if list_id in BLACKLISTED_LISTS:
            continue

        logger.info('Beginning to scrape "{}"'.format(list_id))
        scrape_list(session, list_id, parallelism, since=since)


def message_to_db_message(message):
    """
    Converts a message object (from scraper) into a Database Message object
    """
    db_message = Message(
        message_id=message.message_id,
        text=message.text,
        sent_at=message.sent_at,
        list_id=message.list_id,
        author=message.author,
        email=message.email,
        thread_parent=message.thread_parent,
        thread_idx=message.thread_idx,
        thread_indent=message.thread_indent,
        page=message.page,
        subject=message.subject
    )
    logger.info("Scraped message: {}".format(message))
    return db_message


def scrape_list(session, list_id, parallelism=1, since=None):
    """
    Scrapes a mailing list into the provided database session
    """
    mailing_list = MailingList(list_id)
    message_generator = mailing_list.messages(since=since)
    logger.info("Initializing Pool with Parallelism: {}".format(parallelism))

    if parallelism > 1:
        pool = Pool(processes=parallelism)
        message_generator = pool.imap(message_to_db_message, message_generator)
    else:
        message_generator = (
            message_to_db_message(m) for m in message_generator
        )

    for i, db_message in enumerate(message_generator):
        session.merge(db_message)
        if i > 0 and i % 100 == 0:
            session.commit()
            logger.info("Committed messages to database")
    session.commit()

    if parallelism > 1:
        pool.close()


def scrape_cmd(parallelism=4, start_at=None, update=None):
    """
    Runs the scraper with the given settings
    """

    engine = create_engine("sqlite:///scraper.db")
    Base.metadata.create_all(engine)

    since = None
    if update:
        since = datetime.now() - timedelta(days=30)

    scrape_all(engine, start_at, parallelism, since=since)


if __name__ == "__main__":
    scrape_cmd()
