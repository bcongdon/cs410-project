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

# Establish SQLite Connection
conn = sqlite3.connect("../scraper.db")
conn.row_factory = lambda cursor, row: {"id": str(row[0]), "content": str(row[1])}
c = conn.cursor()

# Query for Documents
c.execute('SELECT message_id, text from message')
entries = c.fetchall()
for entry in entries:
	writer.add_document(id=entry["id"], content=entry["content"])
writer.commit()

# Search for Documents
with idx.searcher() as searcher:
	query = QueryParser("content", idx.schema).parse('document')
	results = searcher.search(query)
	print(results[0])