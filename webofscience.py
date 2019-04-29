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
        client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl')
        rpp = 100
        request_delay = 1

        with client.settings(extra_http_headers={'Cookie': session_header}):
            query_parameters = {
                "databaseId": "WOS",
                "userQuery": query,
                "queryLanguage": "en"
            }
            retrieve_parameters = {
                "firstRecord": 1,
                "count": rpp
            }

            try:
                result = client.service.search(queryParameters=query_parameters, retrieveParameters=retrieve_parameters)
                num_results = result.recordsFound

                pages = int(num_results / rpp) + 1
                for i in range(0, pages):
                    self.logger.debug(f"WOS query page {i + 1} of {pages}")
                    retrieve_parameters['firstRecord'] = 1 + (i * rpp)
                    results = client.service.search(queryParameters=query_parameters, retrieveParameters=retrieve_parameters)

                    for result in results['records']:
                        dois = dois + self.format_result(result)

                    sleep(request_delay)

                self.logger.debug(f"Processed {num_results}, {self.failures} failures")

            except ZeepFault as e:
                self.logger.error(f"WOS Returned error: {e.message}")

        return dois

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
