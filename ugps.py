import secrets
from storage.persistence import DB
from report.reporting import Reporter
from report.reports import *
from unpaywall import UnpaywallClient, UnpaywallArticleRecord, ThreadedUnpaywallClient
from webofscience import get_dois_from_xlsx, get_dois
import openapc
from ugauthors import UgAuthorUpdater

from ldap import LDAPClient
import argparse
import logging
from habanero import counts


def fetch(db, logger, args):
    """
    Collect and data from various APIs, storing the results in the database.
    """

    db.init_db()
    db.clean_db()

    dois = []
    if args.in_file:
        dois = get_dois_from_xlsx('input/wos.xlsx')
    else:
        dois = get_dois()


    results = [] # Threaded clients will append results to this list.
    uc = ThreadedUnpaywallClient(results, args.email, logger=logger)
    queue = uc.get_queue()

    for doi in dois:
        queue.put(doi)

    del dois

    # Block while we wait for the threads to do their thing
    while not queue.empty():
        continue

    uc.stop()

    # Further processing of the results.
    for result in results:
        record = UnpaywallArticleRecord(result)
        citations = counts.citation_count(record.get_doi())
        record.set_metadata('citations', citations)
        db.persist(record)

    # Use OpenAPC to endpoint to fetch average APC costs for each publisher
    oapc = openapc.OpenAPC()
    oapc.fetch_data()

    # Identify local authors by searching for matches in the LDAP directory
    ldap_client = LDAPClient(secrets.LDAP_ENDPOINT, secrets.LDAP_PORT, secrets.LDAP_BASEDN, secrets.LDAP_USER, secrets.LDAP_PASS)
    ug_author_updater = UgAuthorUpdater(ldap_client)
    ug_author_updater.update_authors()


def report(report, outfile=None):
    """
    Generate reports
    :param report: The name of the report to generate.
    :param outfile:
    :return:
    """

    # Reporter manages and runs the available reports.
    # It will automatically pick up any reports that implement the Report interface.
    reporter = Reporter(outfile)
    reporter.register_all()

    if report == 'list':
        for r in reporter.list():
            print(r)
    elif report == 'all':
        reporter.all()
    else:
        reporter.report(report)

# Set up command line arguments.
cli = argparse.ArgumentParser(description='Fetch UG OA data and run reports.')
cli.add_argument('--fetch', action='store_true', help='Fetch data from data sources.')
cli.add_argument('--email', '-e', action='store', default=secrets.UNPAYWALL_EMAIL)
cli.add_argument('--wosuser', action='store', default=secrets.WOS_USER)
cli.add_argument('--wospass', action='store', default=secrets.WOS_PASS)
cli.add_argument('--in_file', '-i', action='store')
cli.add_argument('-v', action='store_true')
cli.add_argument('-vv', action='store_true')

cli.add_argument('--report', action='store', help='Run reports', nargs='?', const="list", default=False)
cli.add_argument('--output', '-o', action='store', default=None)
args = cli.parse_args()

# Set up our logging
logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))
handler.setLevel(logging.DEBUG)

db = DB(logger)

if args.v:
    logger.setLevel(logging.INFO)
elif args.vv:
    logger.setLevel(logging.DEBUG)

handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))
logger.addHandler(handler)

if args.fetch:
    fetch(db, logger, args)

if args.report:
    report(args.report, args.output)
