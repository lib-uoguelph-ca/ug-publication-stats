from zeep import Client
from zeep.exceptions import Fault as ZeepFault
import secrets
from time import sleep
from base64 import b64encode


class WebOfScienceClient:

    def __init__(self, logger):
        self.session = self.get_session()
        self.logger = logger
        self.failures = 0
        self.rpp = 100

        self.query_parameters = {
            "databaseId": "WOS",
            "userQuery": '',
            "queryLanguage": "en"
        }

        self.retrieve_parameters = {
            "firstRecord": 1,
            "count": self.rpp
        }

        self.client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl')


    def get_dois(self, query):
        """
        Get a list of UG DOIs from the Web of Science API.
        :return: a list of DOIs
        """
        dois = []

        session_header = f"SID={self.session}"

        with self.client.settings(extra_http_headers={'Cookie': session_header}):

            num_results = self.do_query(query)

            pages = int(num_results / self.rpp) + 1
            for i in range(0, pages):
                self.logger.info(f"WOS query page {i + 1} of {pages}")
                self.retrieve_parameters['firstRecord'] = 1 + (i * self.rpp)

                retry_wos_query = retry(self.client.service.search, logger=self.logger)
                results = retry_wos_query(
                    queryParameters=self.query_parameters,
                    retrieveParameters=self.retrieve_parameters
                )

                for result in results['records']:
                    dois = dois + self.format_result(result)

            self.logger.debug(f"Processed {num_results}, {self.failures} failures")

        return dois

    def do_query(self, query):
        """
        Do the query and return the number of results returned.
        :return: The number of results returned by the query.
        """

        self.query_parameters['userQuery'] = query

        num_results = 0
        # Function decorator to retry the API calls in case of an error.
        retry_query = retry(self.client.service.search, logger=self.logger)

        try:
            result = retry_query(queryParameters=self.query_parameters, retrieveParameters=self.retrieve_parameters)
            num_results = result.recordsFound
        except ZeepFault as e:
            self.logger.error(f"WOS Returned error: {e.message}")

        return num_results

    def get_session(self):
        """
        Query the WoS api to get a session identifier.
        :return: The session identifier.
        """

        auth_user = (b64encode(f"{secrets.WOS_USER}:{secrets.WOS_PASS}".encode('utf8'))).decode('utf8')
        auth_header = f"Basic {auth_user}"
        client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl')

        result = None
        with client.settings(extra_http_headers={'Authorization': auth_header}):
            result = client.service.authenticate()

        return result

    def format_result(self, item):
        """
        Gets a list of DOIs from a WoS query result.
        :param item: A result from the WoS search query
        :return: A list of DOIs associated with the item.
        """
        metadata = item['other']

        identifiers = []

        for data in metadata:
            if "Doi" in data['label']:
                identifiers = identifiers + data['value']

        if len(identifiers) == 0:
            self.logger.debug(f"Couldn't find DOI")
            self.failures = self.failures + 1

        return identifiers


def get_dois_from_xlsx(file):
    import pandas as pd

    data = pd.read_excel(file)
    data.dropna(subset=['DI'], inplace=True)
    return data['DI']


def retry(func, max=3, logger=None):
    """
    A function decorator, that wraps a function call in logic to retry the call if an exception is thrown.

    :param func: The function to attempt
    :param max: The maximum number of attempts to make
    :param logger: Optional logger for debug information.
    :return: A retry function.
    """

    def retry_function(*args, **kwargs):
        retries = 0
        while True:
            try:
                results = func(*args, **kwargs)
                return results
            except Exception as e:

                if logger:
                    logger.debug(f"Retry error: {e.message}. Trying again ({retries + 1} of {max}  attempts)")

                retries = retries + 1

                if retries >= max:
                    raise Exception("Too many retries.")

                sleep(1)

                continue

    return retry_function
