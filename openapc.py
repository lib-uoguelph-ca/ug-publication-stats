import requests
import logging

from models import Publisher


class OpenAPC:

    def __init__(self):
        self.logger = logging.getLogger('UGPS')

    def fetch_data(self):
        uri = "https://olap.intact-project.org/cube/combined/aggregate?drilldown=publisher&cut=&order=apc_amount_avg%3Adesc"
        r = requests.get(uri)

        data = r.json()

        for row in data['cells']:
            publisher = Publisher.get_or_none(name=row['publisher'])
            self.logger.debug(f"Open APC Lookup - {row['publisher']}")
            if publisher:
                self.logger.debug("Matched Publisher")
                publisher.average_apc = row['apc_amount_avg']
                publisher.save()
