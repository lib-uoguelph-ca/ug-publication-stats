import secrets
from storage.persistence import DB
from report.reporting import Reporter
from report.reports import *
from unpaywall import UnpaywallClient, UnpaywallArticleRecord, ThreadedUnpaywallClient
import openapc
from ugauthors import UgAuthorUpdater
from doaj import DOAJClient
import apc
from webofscience import WebOfScienceClient, get_dois_from_xlsx

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
        dois = get_dois_from_xlsx(args.in_file)
    else:
        wos_client = WebOfScienceClient()
        dois = wos_client.get_dois("OG=University of Guelph")

    results = []  # Threaded clients will append results to this list.
    uc = ThreadedUnpaywallClient(results, args.email, logger=logger, num_threads=6)
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

    # Update APCs for journals and publishers.
    apc_updater = apc.APCUpdater(logger)
    apc_updater.update()

    # Identify local authors by searching for matches in the LDAP directory
    ldap_client = LDAPClient(
        secrets.LDAP_ENDPOINT,
        secrets.LDAP_PORT,
        secrets.LDAP_BASEDN,
        secrets.LDAP_USER,
        secrets.LDAP_PASS
    )
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
cli.add_argument('--email', '-e', action='store', default=secrets.UNPAYWALL_EMAIL, help='Email used to communicate with the Unpaywall API.')
cli.add_argument('--wosuser', action='store', default=secrets.WOS_USER, help='Web of Science user ID')
cli.add_argument('--wospass', action='store', default=secrets.WOS_PASS, help='Web of Science password')
cli.add_argument('--in_file', '-i', action='store', help='Input file (exported from web of science search)')
cli.add_argument('-v', action='store_true')
cli.add_argument('-vv', action='store_true')

cli.add_argument('--report', action='store', help='Name of report to run.', nargs='?', const="list", default=False)
cli.add_argument('--output', '-o', action='store', default=None, help='Directory in which to write reports.')
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



