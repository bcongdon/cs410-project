from bs4 import BeautifulSoup
import requests
from .mailing_list import MailingList
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import Base, Message
from multiprocessing import Pool
import argparse
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_list_ids():
    '''
    Returns a list of all message lists (i.e. topics) from mail;
    '''
    req = requests.get('https://mail.python.org/mailman/listinfo')
    soup = BeautifulSoup(req.text, 'lxml')
    for row in soup.find('table').find_all('tr')[4:]:
        link = row.find('a', href=True)['href']
        yield link.split('/')[-1]


def scrape_all(engine, start_at=None, parallelism=1):
    '''
    Scrape all mailing lists on mail.python.org
    '''
    session = sessionmaker(bind=engine)()

    for list_id in get_list_ids():
        if start_at is not None and list_id < start_at:
            continue
        logger.info('Beginning to scrape "{}"'.format(list_id))
        scrape_list(session, list_id, parallelism)


def message_to_db_message(message):
    '''
    Converts a message object (from scraper) into a Database Message object
    '''
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
        page=message.page
    )
    logger.info("Scraped message: {}".format(message))
    return db_message


def scrape_list(session, list_id, parallelism=1):
    '''
    Scrapes a mailing list into the provided database session
    '''
    mailing_list = MailingList(list_id)
    pool = Pool(processes=parallelism)
    parallel_generator = pool.imap(
        message_to_db_message,
        mailing_list.messages()
    )

    for i, db_message in enumerate(parallel_generator):
        session.merge(db_message)
        if i % 100 == 0:
            session.commit()
            logger.info('Committed messages to database')
    pool.close()


def scrape_cmd():
    '''
    Runs the scraper with the given settings
    '''

    engine = create_engine('sqlite:///scraper.db')
    Base.metadata.create_all(engine)

    parser = argparse.ArgumentParser(description='Python Mailing List Scraper')
    parser.add_argument('--parallelism',
                        default=4, type=int,
                        help='The number of parallel scraping processes to use')
    parser.add_argument('--start_at',
                        help='The mailing list to start at (alphabetically)')
    args = parser.parse_args()

    scrape_all(engine, args.start_at, args.parallelism)


if __name__ == '__main__':
    scrape_cmd()