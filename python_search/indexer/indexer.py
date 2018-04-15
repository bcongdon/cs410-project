import sqlite3
import os.path
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.query import *
from whoosh.qparser import QueryParser
from dateutil.parser import parse as dateparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from ..scraper.model import Message

# Setup Index
schema = Schema(
    list_id=ID(stored=True),
    message_id=ID(stored=True),
    content=TEXT(stored=True),
    author=TEXT(stored=True),
    sent_at=DATETIME(stored=True),
)


def open_index(index_dir):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        return index.create_in(index_dir, schema)
    else:
        return index.open_dir(index_dir)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# # Establish SQLite Connection

# c = conn.cursor()

# # Query for Documents
# count = c.execute('SELECT count(*) as c from message where list_id="python-dev"').fetchone()['c']
# entries = c.execute('SELECT message_id, list_id, author, sent_at, text from message where list_id="python-dev"')
# with tqdm(total=count) as pbar:
#     for i, entry in enumerate(entries):


BLACKLISTED_LISTS = []


def update_index(session, index):
    print("Calculating query size...")
    query = session.query(Message).filter(Message.sent_at > '2016-01-01').filter_by(list_id='python-dev')
    count = query.count()
    writer = index.writer()

    with tqdm(total=count) as pbar:
        for idx, message in enumerate(query.yield_per(100)):
            pbar.update(1)
            writer.add_document(
                list_id=message.list_id,
                message_id=message.message_id,
                content=message.text,
                author=message.author,
                sent_at=message.sent_at
            )
            if idx % 10000 == 0 and idx != 0:
                pbar.write("Comitting at doc {}...".format(idx))
                writer.commit()
                writer = index.writer()
            pbar.write("Comitting at doc {}...".format(idx+1))
        writer.commit()


def index_cmd(db, index_dir):
    index = open_index(index_dir)

    engine = create_engine("sqlite:///{}".format(db))
    session = sessionmaker(bind=engine)()

    update_index(session, index)


class IndexSearcher:
    def __init__(self, index_dir):
        self.index = open_index(index_dir)

    def search(self, query_str, page=1, n=10):
        with self.index.searcher() as searcher:
            query = QueryParser("content", self.index.schema).parse(query_str)

            results = searcher.search_page(query, page, pagelen=n)
            for result in results:
                yield result['list_id'], result['message_id'], result['content'], result['author'], result['sent_at'].strftime('%m/%d/%Y')
