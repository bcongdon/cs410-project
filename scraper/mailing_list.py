from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import time
import logging
from message import Message
from util import format_month

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)

BASE_URL = 'https://mail.python.org/pipermail/'

class MailingList:

    """Representation of a mailing list
    
    Attributes
    ----------
    list_id : str
        The list_id of the mailing list
    """
    
    def __init__(self, list_id):
        """Constructs a new mailing list
        
        Parameters
        ----------
        list_id : str
            The list_id of the mailing list
        """
        self.list_id = list_id.lower()
        self._soup = None

    @property
    def soup(self):
        """Requests the summary page of the mailing list, and returns a BeautifulSoup soup object

        Caches the page data once fetched
        
        Returns
        -------
        bs4.BeautifulSoup
            The soup of the mailing list summary page
        """
        if self._soup is not None:
            return self._soup

        req = requests.get(BASE_URL + self.list_id)
        self._soup = BeautifulSoup(req.text, 'lxml')
        return self._soup

    def _message_link_to_id(self, link):
        """Parses a message link to a message id

        Takes a link of form "123.html" and returns just the id - "123"
        
        Parameters
        ----------
        link : str
            The message link
        
        Returns
        -------
        str
            The parsed messsage id
        """
        return link.split('.')[0]

    def _scrape_month(self, month):
        """Scrapes all the messages from this mailing list that were posted during the given month
        
        Parameters
        ----------
        month : Date
            The month to scrape
        
        Yields
        ------
        Message
            The scraped message
        """
        logger.info('Scraping "{}" for month {}'.format(self.list_id, format_month(month)))

        req = requests.get('/'.join(
            [BASE_URL, self.list_id, format_month(month), 'thread.html']
        ))
        soup = BeautifulSoup(req.text, 'lxml')
        thread_ul = soup.find_all('ul')[1]

        for thread in thread_ul.find_all('li', recursive=False):
            thread_id = self._message_link_to_id(thread.find('a', href=True)['href'])
            yield Message(self.list_id, month, thread_id, thread_id, 0, 0)
            
            for child_idx, child in enumerate(thread.find_all('li')):
                depth = 0
                tmp = child
                while tmp != thread:
                    depth += 1
                    tmp = tmp.parent

                child_id = self._message_link_to_id(child.find('a', href=True)['href'])
                yield Message(
                    list_id=self.list_id,
                    month=month,
                    message_id=child_id,
                    thread_parent=thread_id,
                    thread_idx=child_idx + 1,
                    thread_indent=depth)

    def _get_months(self):
        """Returns the months for which there are posts in this mailing list.

        Scrapes the mailing list summary page to get the valid months.
        
        Yields
        ------
        Date
            A valid date for this mailing list, yielded in descending order
        """
        for row in self.soup.find_all('tr')[1:]:
            month_str = row.find('td').text.replace(':', '')
            month = datetime.strptime(month_str, '%B %Y')
            yield month

    def messages(self, month=None):
        """
        Parameters
        ----------
        month : Date, optional
            If provided, `messages` will only yield messages that were posted in this month
        
        Yields
        ------
        Message
            The scraped message, yielded in ascending order of creation time
        
        """

        if month is not None:
            months = [month]
        else:
            months = self._get_months()

        for month in months:
            for message in self._scrape_month(month):
                yield message
            time.sleep(1.0)
        

if __name__ == '__main__':
    for message in MailingList('python-dev').messages():
        print('|'.join([str(message.sent_at), message.author, message.email]))
        time.sleep(1.0)