import urllib.request, urllib.parse
from urllib.error import URLError
import json


class UnpaywallClient:

    def __init__(self, email, logger=None):
        self.logger = logger
        self.email = email
        self.endpoint = 'https://api.unpaywall.org/v2/'

    def lookup(self, doi):
        try:
            request_url = self.endpoint + urllib.parse.quote(doi) + "?email=" + self.email
            response = urllib.request.urlopen(request_url)

        except URLError as error:
            if self.logger:
                self.logger.error(f"Unpaywall request error for doi: {doi} - {error}")

            return None

        data = response.read()
        return json.loads(data)

    def fetchall(self, dois):
        for doi in dois:
            yield self.lookup(doi)
