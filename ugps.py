import logging
from unpaywall import UnpaywallClient, UnpaywallParser
from webofscience import get_dois
from storage import persist, init_db, clean_db
import secrets

init_db()
clean_db()

dois = get_dois()

logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))
logger.addHandler(handler)

uc = UnpaywallClient(secrets.UNPAYWALL_EMAIL, logger)

for result in uc.fetchall(dois):
    if not result:
        continue

    print(result)

    record = UnpaywallParser(result)
    persist(record)


