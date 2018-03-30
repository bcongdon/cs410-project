import sqlite3
import os.path
import petl as etl
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.query import *
from whoosh.qparser import QueryParser

# Setup Index
schema = Schema(id=ID(stored=True), content=TEXT)
if not os.path.exists("index"):
    os.mkdir("index")
idx = create_in("index", schema)
writer = idx.writer()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Establish SQLite Connection
conn = sqlite3.connect("../scraper.db")
conn.row_factory = dict_factory
c = conn.cursor()

# Query for Documents
c.execute('SELECT message_id, list_id, text from message')
entries = c.fetchall()
for entry in entries:
    doc_id = "{}-{}".format(entry["list_id"], entry["message_id"])
    writer.add_document(id=doc_id, content=entry["text"])
writer.commit()

# Search for Documents
with idx.searcher() as searcher:
    query = QueryParser("content", idx.schema).parse('python')
    results = searcher.search(query)
    print(list(results))