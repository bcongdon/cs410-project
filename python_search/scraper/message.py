from dateutil.parser import parse
import requests
from bs4 import BeautifulSoup
import logging
import backoff


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://mail.python.org/pipermail"


@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException)
def get_page(url):
    return requests.get(url)


class Message:

    """Representation of a mailing list message
    
    Attributes
    ----------
    list_id : str
        The list the message came from 
    message_id : str
        The message's id
    page : str
        The subpage in which the message was created
    thread_idx : int
        The index of this message in its thread
    thread_parent : str
        The message id of the root parent of this message
    thread_indent: int
        The indent level of this message in its thread
    """

    def __init__(
        self,
        list_id,
        page,
        message_id,
        thread_parent,
        thread_idx,
        thread_indent,
    ):
        """
        Parameters
        ----------
        list_id : str
            The list the message came from 
        message_id : str
            The message's id
        page : str
            The subpage in which the message was created
        thread_idx : int
            The index of this message in its thread
        thread_parent : str
            The message id of the root parent of this message
        thread_indent: int
            The indent level of this message in its thread
        """

        self.list_id = list_id
        self.page = page
        self.message_id = message_id
        self.thread_parent = thread_parent
        self.thread_idx = thread_idx
        self.thread_indent = thread_indent

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

        try:
            url = "/".join(
                    [
                        BASE_URL,
                        self.list_id,
                        self.page,
                        self.message_id + ".html",
                    ]
                )
            req = get_page(url)
            self._soup = BeautifulSoup(req.text, "lxml")
        except:
            logger.warn(
                "Request failed for message {} in list {}".format(
                    self.message_id, self.list_id
                )
            )
        return self._soup

    @property
    def text(self):
        """Scrapes the text of the message
        
        Returns
        -------
        str
            The message text
        """
        pre_elem = self.soup.find("pre")
        if pre_elem is None:
            logger.warn(
                "Couldn't find message text for message {} in list {}".format(
                    self.message_id, self.list_id
                )
            )
            return None

        return pre_elem.text.strip()

    @property
    def sent_at(self):
        """Scrapes the sending time of the message
        
        Returns
        -------
        DateTime
            The sent_at time of the message
        """
        sent_at_elem = self.soup.find("i")
        if sent_at_elem is None:
            logger.warn(
                "Couldn't find sent_at for message {} in list {}".format(
                    self.message_id, self.list_id
                )
            )
            return None

        try:
            return parse(sent_at_elem.text)

        except:
            logger.warn(
                "Unable to parse '{}' as a datetime".format(sent_at_elem.text)
            )
            return None

    @property
    def author(self):
        """Scrapes the author name of the message
        
        Returns
        -------
        str
            The author name of the message
        """
        author_elem = self.soup.find("b")
        if author_elem is None:
            logger.warn(
                "Couldn't find author for message {} in list {}".format(
                    self.message_id, self.list_id
                )
            )
            return None

        return author_elem.text.strip()

    @property
    def email(self):
        """Scrapes the sending email of the message
        
        Returns
        -------
        str
            The sending email of the message
        """
        email_elem = self.soup.find("a")
        if email_elem is None:
            logger.warn(
                "Couldn't find email for message {} in list {}".format(
                    self.message_id, self.list_id
                )
            )
            return None

        return email_elem.text.strip()

    @property
    def subject(self):
        """Scrapes the subject of the message
        
        Returns
        -------
        str
            The subject of the message
        """
        subject_elem = self.soup.find("h1")
        if subject_elem is None:
            logger.warn(
                "Couldn't find subject for message {} in list {}".format(
                    self.message_id, self.list_id
                )
            )
            return None

        return subject_elem.text.strip()


    def __str__(self):
        return "<Message - List: {}, Page: {}, ID: {}>".format(
            self.list_id, self.page, self.message_id
        )

    def __repr__(self):
        return self.__str__()
