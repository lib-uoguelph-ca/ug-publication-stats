from abc import ABC


class BaseRecord(ABC):
    metadata = {}

    def _get_value(self, key):
        if key in self.metadata:
            return self.metadata[key]

        return None


class BaseArticleRecord(BaseRecord):

        def set_metadata(self, name, value):
            self.metadata[name] = value

        def get_title(self):
            return self._get_value('title')

        def get_date(self):
            return self._get_value('date')

        def get_year(self):
            return self._get_value('year')

        def get_journal_title(self):
            return self._get_value('journal')

        def get_type(self):
            return self._get_value('type')

        def get_publisher(self):
            return self._get_value('publisher')

        def is_oa(self):
            return self._get_value('oa')

        def is_hybrid(self):
            return self._get_value('hybrid')

        def is_bronze(self):
            return self._get_value('bronze')

        def get_self_archived(self):
            return self._get_value('self_archived')

        def get_self_archived_count(self):
            return self._get_value('self_archived_count')

        def get_doi(self):
            return self._get_value('doi')

        def get_doi_url(self):
            return self._get_value('doi_url')

        def get_locations(self):
            return self._get_value('locations')

        def get_authors(self):
            return self._get_value('authors')

        def get_citations(self):
            return self._get_value('citations')


class BaseAuthorRecord(BaseRecord):

    def get_first_name(self):
        return self._get_value('first_name')

    def get_last_name(self):
        return self._get_value('last_name')

    def get_orcid(self):
        return self._get_value('orcid')

    def get_affiliations(self):
        return self._get_value('affiliations')

