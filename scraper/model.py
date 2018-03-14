from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'message'
    message_id = Column(String, primary_key=True)
    text = Column(String)
    sent_at = Column(DateTime)
    list_id = Column(String, primary_key=True)
    author = Column(String)
    email = Column(String)

    thread_parent = Column(Integer)
    thread_idx = Column(Integer)