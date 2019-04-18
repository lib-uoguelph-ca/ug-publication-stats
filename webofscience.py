from zeep import Client
import secrets
from base64 import b64encode

def get_dois():
    """
    Get a list of UG DOIs from the Web of Science API.
    :return: a list of DOIs
    """
    dois = []
    # with WosClient(secrets.WOS_USER, secrets.WOS_PASS, lite=True) as client:
    #     result = wos.utils.query(client, 'OG=University of Guelph')
    #     print(result)
    session = get_session()

    session_header = f"SID={session}"
    client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl')
    with client.settings(extra_http_headers={'Cookie': session_header}):
        query_parameters = {
            "databaseId": "WOS",
            "userQuery": "OG=University of Guelph",
            "queryLanguage": "en"
        }
        retrieve_parameters = {
            "firstRecord": 1,
            "count": 100
        }
        result = client.service.search(queryParameters=query_parameters, retrieveParameters=retrieve_parameters)
        pass


def get_session():
    auth_user = (b64encode(f"{secrets.WOS_USER}:{secrets.WOS_PASS}".encode('utf8'))).decode('utf8')
    auth_header = f"Basic {auth_user}"
    client = Client('http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl')

    result = None
    with client.settings(extra_http_headers={'Authorization': auth_header}):
        result = client.service.authenticate()
        pass

    return result

def format_result(item):
    pass


def get_dois_from_xlsx(file):
    import pandas as pd

    data = pd.read_excel(file)
    data.dropna(subset=['DI'], inplace=True)
    return data['DI']
