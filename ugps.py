from wos import WosClient
import wos.utils
import logging

import secrets
from unpaywall import UnpaywallClient, UnpaywallParser
from storage import persist, init_db, clean_db


# with WosClient(secrets.WOS_USER, secrets.WOS_PASS) as client:
#     print(wos.utils.query(client, 'OG="University of Guelph"'))


def get_dois():
    """
    Get a list of UG DOIs from the Web of Science API.
    :return: a list of DOIs
    """

    # We're just stubbing this out for now, because WOS hasn't approved my developer application yet.
    dois = ["10.1016/j.tourman.2018.10.025",
            "10.1098/rspb.2002.2218",
            "10.1038/nature11234",
            "10.1021/cr00104a001",
            "10.1111/j.1471-8286.2006.01678.x"]

    return dois


init_db()
clean_db()


dois = get_dois()

logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))
logger.addHandler(handler)

uc = UnpaywallClient('doana@uoguelph.ca', logger)

for result in uc.fetchall(dois):

    if not result:
        continue

    print(result)

    record = UnpaywallParser(result)
    persist(record)


