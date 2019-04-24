from zeep import Client
import secrets
from base64 import b64encode


class WebOfScienceClient:

    def __init__(self):
        self.session = self.get_session()

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
            result = client.service.search(queryParameters=query_parameters, retrieveParameters=retrieve_parameters)
            num_results = result.recordsFound

            for i in range(rpp, num_results, rpp):
                retrieve_parameters['firstRecord'] = i
                results = client.service.search(queryParameters=query_parameters, retrieveParameters=retrieve_parameters)

                for result in results['records']:
                    dois = dois + self.format_result(result)

        return dois

    def get_session(self):
        auth_user = (b64encode(f"{secrets.WOS_USER}:{secrets.WOS_PASS}".encode('utf8'))).decode('utf8')
        auth_header = f"Basic {auth_user}"
        client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl')

        result = None
        with client.settings(extra_http_headers={'Authorization': auth_header}):
            result = client.service.authenticate()
            pass

        return result

    def format_result(self, item):
        metadata = item['other']

        identifiers = []
        for data in metadata:
            if data['label'] == 'Identifier.Xref_Doi':
                identifiers = identifiers + data['value']

        return identifiers


def get_dois_from_xlsx(self, file):
    import pandas as pd

    data = pd.read_excel(file)
    data.dropna(subset=['DI'], inplace=True)
    return data['DI']
