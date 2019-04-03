import requests
import logging

from models import Publisher, Journal


class OpenAPC:
    """
    Fetch and save data from OpenAPC on average APC costs for each publisher.
    """

    def __init__(self):
        self.logger = logging.getLogger('UGPS')

    def fetch_data(self):
        self.update_publisher_data()
        self.update_journal_data()

    def get_publisher_data(self):
        uri = "https://olap.intact-project.org/cube/combined/aggregate?drilldown=publisher&cut=&order=apc_amount_avg%3Adesc"
        r = requests.get(uri)
        data = r.json()
        return data['cells']

    def update_publisher_data(self, data=None):
        data = self.get_publisher_data()

        for row in data:
            publisher = Publisher.get_or_none(name=row['publisher'])
            self.logger.debug(f"Open APC Publisher Lookup - {row['publisher']}")
            if publisher:
                self.logger.debug("Matched Publisher")
                publisher.average_apc = row['apc_amount_avg']
                publisher.save()

    def get_journal_data(self):
        uri = "https://olap.intact-project.org/cube/combined/aggregate?drilldown=journal_full_title&cut=&order=apc_amount_avg%3Adesc"
        r = requests.get(uri)
        data = r.json()
        return data['cells']

    def update_journal_data(self):
        data = self.get_journal_data()

        for row in data:
            journal = Journal.get_or_none(name=row['journal_full_title'])
            self.logger.debug(f"Open APC Journal Lookup - {row['journal_full_title']}")
            if journal:
                self.logger.debug("Matched Journal")
                journal.average_apc = row['apc_amount_avg']
                journal.save()
