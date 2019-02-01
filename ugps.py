import argparse
import logging
from unpaywall import UnpaywallClient, UnpaywallParser
from webofscience import get_dois
from storage import persist, init_db, clean_db
import secrets

logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))
logger.addHandler(handler)


def fetch(logger):
    init_db()
    clean_db()

    dois = get_dois()
    uc = UnpaywallClient(secrets.UNPAYWALL_EMAIL, logger)
    for result in uc.fetchall(dois):
        if not result:
            continue

        doi = result['doi']
        logger.debug(f"Unpaywall: Fetching DOI: {doi}")
        record = UnpaywallParser(result)
        persist(record)


cli = argparse.ArgumentParser(description='Fetch UG OA data and run reports.')
cli.add_argument('--fetch', action='store_true', help='Fetch data from data sources.')
cli.add_argument('-e', action='store', default=secrets.UNPAYWALL_EMAIL)
cli.add_argument('-wosuser', action='store', default=secrets.WOS_USER)
cli.add_argument('-wospass', action='store', default=secrets.WOS_PASS)
cli.add_argument('-v', action='store_true')
cli.add_argument('-vv', action='store_true')
args = cli.parse_args()


logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
handler.setLevel(logging.DEBUG)

if args.v:
    logger.setLevel(logging.INFO)
elif args.vv:
    logger.setLevel(logging.DEBUG)

handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))
logger.addHandler(handler)

if args.fetch:
    fetch(logger)
