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
        self.fetch_publisher_data()
        self.fetch_journal_data()

    def fetch_publisher_data(self):
        uri = "https://olap.intact-project.org/cube/combined/aggregate?drilldown=publisher&cut=&order=apc_amount_avg%3Adesc"
        r = requests.get(uri)

        data = r.json()

        for row in data['cells']:
            publisher = Publisher.get_or_none(name=row['publisher'])
            self.logger.debug(f"Open APC Publisher Lookup - {row['publisher']}")
            if publisher:
                self.logger.debug("Matched Publisher")
                publisher.average_apc = row['apc_amount_avg']
                publisher.save()

    def fetch_journal_data(self):
        uri = "https://olap.intact-project.org/cube/combined/aggregate?drilldown=journal_full_title&cut=&order=apc_amount_avg%3Adesc"
        r = requests.get(uri)

        data = r.json()

        for row in data['cells']:
            journal = Journal.get_or_none(name=row['journal_full_title'])
            self.logger.debug(f"Open APC Journal Lookup - {row['journal_full_title']}")
            if journal:
                self.logger.debug("Matched Journal")
                journal.average_apc = row['apc_amount_avg']
                journal.save()
