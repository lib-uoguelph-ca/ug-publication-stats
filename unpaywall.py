import urllib.request, urllib.parse
from urllib.error import URLError
import json
from storage.record import BaseRecord


class UnpaywallClient:

    def __init__(self, email, logger=None):
        self.logger = logger
        self.email = email
        self.endpoint = 'https://api.unpaywall.org/v2/'

    def lookup(self, doi):
        self.logger.debug(f"Unpaywall: Fetching DOI: {doi}")

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


class UnpaywallParser(BaseRecord):

    def __init__(self, record):
        self.hybrid = False
        self.bronze = False
        self.green = 0

        self.preprocess(record)

    def preprocess(self, record):

        self.metadata['title'] = record['title']
        self.metadata['date'] = record['published_date']
        self.metadata['year'] = record['year']
        self.metadata['journal'] = record['journal_name']
        self.metadata['type'] = record['genre']
        self.metadata['publisher'] = record['publisher']
        self.metadata['is_oa'] = record['is_oa']
        self.metadata['doi'] = record['doi']
        self.metadata['doi_url'] = record['doi_url']
        self.metadata['locations'] = record['oa_locations']
        self.metadata['authors'] = self._get_authors(record)

        self._set_flags(record)

        self.metadata['hybrid'] = self.hybrid
        self.metadata['bronze'] = self.bronze
        self.metadata['self_archived'] = self.green

    def _set_flags(self, record):
        """
        Scan through the record and:
        - Set various flags relating to the style of OA.
        - Count how many green OA locations there are

        This way we don't have to do this every time we want to look up this information.
        """
        if not self.is_oa():
            return

        locations = self.get_locations()

        # If the record is in DOAJ or flagged as OA it's gold
        gold = False
        if record['journal_is_in_doaj'] or record['journal_is_oa']:
            gold = True

        for loc in locations:
            # If it has a location that is of type 'repository' it's green
            if loc['host_type'] == 'repository':
                self.green += 1

            # If the host is a publisher and it has no license, it's bronze
            # If it has a license that's not a creative commons license, it's bronze
            # If it has a creative commons license, it's hybrid.
            if not gold and loc['host_type'] == 'publisher':
                if not loc['license']:
                    self.bronze = True

                if loc['license'] and loc['license'][0:2] == 'cc':
                    self.hybrid = True
                else:
                    self.bronze = True

    def _get_authors(self, record):
        if not record['z_authors']:
            return []

        authors = [UnpaywallAuthor(author) for author in record['z_authors']]
        return authors


class UnpaywallAuthor:
    def __init__(self, author):
        self.record = author

    def get_first_name(self):
        return self.get_value('given')

    def get_last_name(self):
        return self.get_value('family')

    def get_orcid(self):
        return self.get_value('ORCID')

    def get_affiliations(self):
        values = self.get_value('affiliation')

        if not values:
            return None

        results = [value['name'] for value in values]

        return '; '.join(results)


    def get_value(self, key):
        if key in self.record:
            return self.record[key]

        return None