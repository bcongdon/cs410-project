import os.path
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.qparser import QueryParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from ..scraper.model import Message
from .cleaning import clean_message

# Setup Index
schema = Schema(
    list_id=ID(stored=True),
    message_id=ID(stored=True),
    content=TEXT(stored=True),
    author=TEXT(stored=True),
    sent_at=DATETIME(stored=True),
    thread_parent=ID(stored=True),
    thread_idx=ID(stored=True)
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
                content=clean_message(message.text),
                author=message.author,
                sent_at=message.sent_at,
                thread_parent=str(message.thread_parent),
                thread_idx=str(message.thread_idx)
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
                yield result['list_id'], result['message_id'], result['content'], result['author'], result['sent_at'].strftime('%m/%d/%Y'), result['thread_parent'], result['thread_idx']

    def search_for_thread(self, query_str):
        with self.index.searcher() as searcher:
            query = QueryParser("thread_parent", self.index.schema).parse(query_str)

            results = searcher.search(query, limit=None)
            for result in results:
                yield result['list_id'], result['message_id'], result['content'], result['author'], result['sent_at'].strftime('%m/%d/%Y'), result['thread_parent'], result['thread_idx']
