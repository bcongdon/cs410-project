import sqlite3
import os.path
import petl as etl
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.query import *
from whoosh.qparser import QueryParser
from dateutil.parser import parse as dateparse

# Setup Index
schema = Schema(
    list_id=ID(stored=True),
    message_id=ID(stored=True),
    content=TEXT,
    author=TEXT,
    sent_at=DATETIME
)

if not os.path.exists('index'):
    os.mkdir('index')
idx = create_in('index', schema)
writer = idx.writer()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Establish SQLite Connection
conn = sqlite3.connect('../scraper.db')
conn.row_factory = dict_factory
c = conn.cursor()

# Query for Documents
c.execute('SELECT message_id, list_id, author, sent_at, text from message')
entries = c.fetchall()
for entry in entries:
    writer.add_document(
        list_id=entry['list_id'],
        message_id=entry['message_id'],
        content=entry['text'],
        author=entry['author'],
        sent_at=dateparse(entry['sent_at'])
    )
writer.commit()

# Search for Documents
with idx.searcher() as searcher:
    query = QueryParser('content', idx.schema).parse('python')
    results = searcher.search(query)
    print(list(results))