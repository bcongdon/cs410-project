from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup
from util import format_month

BASE_URL = 'https://mail.python.org/pipermail'

class Message:

    """Representation of a mailing list message
    
    Attributes
    ----------
    list_id : str
        The list the message came from 
    message_id : str
        The message's id
    month : Date
        The month in which the message was created
    thread_idx : int
        The index of this message in its thread
    thread_parent : str
        The message id of the root parent of this message
    thread_indent: int
        The indent level of this message in its thread
    """
    
    def __init__(self, list_id, month, message_id, thread_parent, thread_idx, thread_indent):
        """
        Parameters
        ----------
        list_id : str
            The list the message came from 
        message_id : str
            The message's id
        month : Date
            The month in which the message was created
        thread_idx : int
            The index of this message in its thread
        thread_parent : str
            The message id of the root parent of this message
        thread_indent: int
            The indent level of this message in its thread
        """

        self.list_id = list_id
        self.month = month
        self.message_id = message_id
        self.thread_parent = thread_parent
        self.thread_idx = thread_idx

        self._soup = None

    @property
    def soup(self):
        """Requests the content page of the message, and returns a BeautifulSoup soup object
        
        Caches the page data once fetched
        
        Returns
        -------
        bs4.BeautifulSoup
            The soup of the message content page
        """
        if self._soup is not None:
            return self._soup

        req = requests.get('/'.join(
            [BASE_URL, self.list_id, format_month(self.month), self.message_id + '.html']))
        self._soup = BeautifulSoup(req.text, 'lxml')
        return self._soup

    @property
    def text(self):
        """Scrapes the text of the message
        
        Returns
        -------
        str
            The message text
        """
        return self.soup.find('pre').text.strip()

    @property
    def sent_at(self):
        """Scrapes the sending time of the message
        
        Returns
        -------
        DateTime
            The sent_at time of the message
        """
        return parse(self.soup.find('i').text)

    @property
    def author(self):
        """Scrapes the author name of the message
        
        Returns
        -------
        str
            The author name of the message
        """
        return self.soup.find('b').text.strip()

    @property
    def email(self):
        """Scrapes the sending email of the message
        
        Returns
        -------
        str
            The sending email of the message
        """
        return self.soup.find('a').text.strip()

    def __str__(self):
        return "<Message - List: {}, Month: {}, ID: {}>".format(
            self.list_id, self.month, self.message_id)

    def __repr__(self):
        return self.__str__()
