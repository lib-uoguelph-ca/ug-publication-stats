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
        # with WosClient(secrets.WOS_USER, secrets.WOS_PASS, lite=True) as client:
        #     result = wos.utils.query(client, 'OG=University of Guelph')
        #     print(result)

        session_header = f"SID={self.session}"
        request_delay = 1
        self.query_parameters['userQuery'] = query

        with self.client.settings(extra_http_headers={'Cookie': session_header}):

            num_results = self.get_num_results()

            pages = int(num_results / self.rpp) + 1
            for i in range(0, pages):
                self.logger.debug(f"WOS query page {i + 1} of {pages}")
                self.retrieve_parameters['firstRecord'] = 1 + (i * self.rpp)

                retry_wos_query = retry(self.client.service.search)
                results = retry_wos_query(queryParameters=self.query_parameters, retrieveParameters=self.retrieve_parameters)

                for result in results['records']:
                    dois = dois + self.format_result(result)

                sleep(request_delay)

            self.logger.debug(f"Processed {num_results}, {self.failures} failures")

        return dois

    def get_num_results(self):
        num_results = 0

        try:
            result = self.client.service.search(queryParameters=self.query_parameters, retrieveParameters=self.retrieve_parameters)
            num_results = result.recordsFound
        except ZeepFault as e:
            self.logger.error(f"WOS Returned error: {e.message}")

        return num_results


    def get_session(self):
        auth_user = (b64encode(f"{secrets.WOS_USER}:{secrets.WOS_PASS}".encode('utf8'))).decode('utf8')
        auth_header = f"Basic {auth_user}"
        client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl')

        result = None
        with client.settings(extra_http_headers={'Authorization': auth_header}):
            result = client.service.authenticate()

        return result

    def format_result(self, item):
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
                    logger.debug(f"Retry error: {e.message}. Trying again ({retry + 1} of {max}  attempts)")

                retries = retries + 1

                if retries >= max:
                    raise Exception("Too many retries.")

                continue

    return retry_function
