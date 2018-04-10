import sqlite3
import os.path
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.query import *
from whoosh.qparser import QueryParser
from dateutil.parser import parse as dateparse
from tqdm import tqdm

# Setup Index
schema = Schema(
    list_id=ID(stored=True),
    message_id=ID(stored=True),
    content=TEXT,
    author=TEXT,
    sent_at=DATETIME,
)

# if not os.path.exists('index'):
#     os.mkdir('index')
# idx = create_in('index', schema)
# writer = idx.writer()

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

# # Establish SQLite Connection
# conn = sqlite3.connect('./scraper.db')
# conn.row_factory = dict_factory
# c = conn.cursor()

# # Query for Documents
# count = c.execute('SELECT count(*) as c from message where list_id="python-dev"').fetchone()['c']
# entries = c.execute('SELECT message_id, list_id, author, sent_at, text from message where list_id="python-dev"')
# with tqdm(total=count) as pbar:
#     for i, entry in enumerate(entries):
#         if i > 10000:
#             break
#         pbar.update(1)
#         writer.add_document(
#             list_id=entry['list_id'],
#             message_id=entry['message_id'],
#             content=entry['text'],
#             author=entry['author'],
#             sent_at=dateparse(entry['sent_at']) if entry['sent_at'] else None
#         )
#         if i % 10000 == 0:
#             writer.commit()
#             writer = idx.writer()
# writer.commit()

# Search for Documents
idx_read = open_dir("index")
with idx_read.searcher() as searcher:
    query = QueryParser("content", idx_read.schema).parse("python")
    results = searcher.search(query)
    print(results)
    print(list(results))
