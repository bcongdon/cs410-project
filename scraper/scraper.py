from bs4 import BeautifulSoup
import requests
from mailing_list import MailingList
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Message
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_list_ids():
    req = requests.get('https://mail.python.org/mailman/listinfo')
    soup = BeautifulSoup(req.text, 'lxml')
    for row in soup.find('table').find_all('tr')[4:]:
        link = row.find('a', href=True)['href']
        yield link.split('/')[-1]

def scrape_all(engine):
    session = sessionmaker(bind=engine)()

    for list_id in get_list_ids():
        logger.info('Beginning to scrape "{}"'.format(list_id))
        scrape_list(session, list_id)

def scrape_list(session, list_id):
    mailing_list = MailingList(list_id)
    for i, message in enumerate(mailing_list.messages()):
        logger.info("Scraped message: {}".format(message))
        db_message = Message(
            message_id=message.message_id,
            text=message.text,
            sent_at=message.sent_at,
            list_id=message.list_id,
            author=message.author,
            email=message.email,
            thread_parent=message.thread_parent,
            thread_idx=message.thread_idx,
        )
        session.merge(db_message)
        if i % 100 == 0:
            session.commit()
            logger.info('Committed messages to database')


if __name__ == '__main__':
    engine = create_engine('sqlite:///scraper.db')
    Base.metadata.create_all(engine)

    scrape_all(engine)
    