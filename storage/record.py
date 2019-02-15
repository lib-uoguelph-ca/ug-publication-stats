from abc import ABC


class BaseRecord(ABC):

        metadata = {}

        def get_title(self):
            return self.metadata['title']

        def get_date(self):
            return self.metadata['date']

        def get_year(self):
            return self.metadata['year']

        def get_journal_title(self):
            return self.metadata['journal']

        def get_type(self):
            return self.metadata['type']

        def get_publisher(self):
            return self.metadata['publisher']

        def is_oa(self):
            return self.metadata['is_oa']

        def is_hybrid(self):
            # self.hybrid is set during preprocess()
            return self.metadata['hybrid']

        def is_bronze(self):
            # self.bronze is set during preprocess()
            return self.metadata['bronze']

        def get_self_archived(self):
            # self.green is set during preprocess()
            return self.metadata['self_archived']

        def get_doi(self):
            return self.metadata['doi']

        def get_doi_url(self):
            return self.metadata['doi_url']

        def get_locations(self):
            return self.metadata['locations']

        def get_authors(self):
            return self.metadata['authors']
