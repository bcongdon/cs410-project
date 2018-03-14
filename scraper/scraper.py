from bs4 import BeautifulSoup
import requests
from mailing_list import MailingList
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Message


def get_list_ids():
    req = requests.get('https://mail.python.org/mailman/listinfo')
    soup = BeautifulSoup(req.text, 'lxml')
    for row in soup.find('table').find_all('tr')[4:]:
        link = row.find('a', href=True)['href']
        yield link.split('/')[-1]

def scrape_all(engine):
    session = sessionmaker(bind=engine)()

    for list_id in get_list_ids():
        mailing_list = MailingList(list_id)
        for i, message in enumerate(mailing_list.messages()):
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


if __name__ == '__main__':
    engine = create_engine('sqlite:///scraper.db')
    Base.metadata.create_all(engine)

    scrape_all(engine)
    