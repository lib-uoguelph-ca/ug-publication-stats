import urllib.parse
import requests


class DOAJClient:

    base_url = "https://doaj.org/api/v1/"

    def __init__(self, logger):
        self.logger = logger

    def get_journal_by_issn(self, issn):
        endpoint = "search/journals/"

        request_url = f"{self.base_url}{endpoint}issn:{urllib.parse.quote(issn)}"

        try:
            response = requests.get(request_url)
            response.raise_for_status()  # Throw exceptions for bad requests

        except requests.exceptions.HTTPError as error:
            if self.logger:
                self.logger.error(f"Unpaywall request error for doi: {doi} - {error}")

            return None

        except TypeError as error:
            if self.logger:
                self.logger.error(f"Can't escape DOI: {doi} - {error}")

            return None

        results = response.json()
        if len(results['results']) == 1:
            return results['results'][0]
        else:
            return None