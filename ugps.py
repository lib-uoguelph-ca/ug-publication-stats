import argparse
import logging
from unpaywall import UnpaywallClient, UnpaywallParser
from webofscience import get_dois_from_xlsx, get_dois
from storage.persistence import DB
import secrets
from report.reporting import Reporter
from report.reports import *

logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%m-%Y %H:%M:%S'))


def fetch(db, logger, args):

    # TODO: Implement threading
    db.init_db()
    db.clean_db()

    dois = []
    if args.in_file:
        dois = get_dois_from_xlsx('input/wos.xlsx')
    else:
        dois = get_dois()

    uc = UnpaywallClient(args.email, logger)
    for doi in dois:
        result = uc.lookup(doi)

        if not result:
            continue

        record = UnpaywallParser(result)
        db.persist(record)


def report(report, outfile):
    reporter = Reporter(outfile)
    reporter.register_all()

    if report == 'list':
        for r in reporter.list():
            print(r)
    elif report == 'all':
        reporter.all()
    else:
        reporter.report(report)


cli = argparse.ArgumentParser(description='Fetch UG OA data and run reports.')
cli.add_argument('--fetch', action='store_true', help='Fetch data from data sources.')
cli.add_argument('--email', '-e', action='store', default=secrets.UNPAYWALL_EMAIL)
cli.add_argument('--wosuser', action='store', default=secrets.WOS_USER)
cli.add_argument('--wospass', action='store', default=secrets.WOS_PASS)
cli.add_argument('--in_file', '-i', action='store')
cli.add_argument('-v', action='store_true')
cli.add_argument('-vv', action='store_true')

cli.add_argument('--report', action='store', help='Run reports', nargs='?', const="list", default=False)
cli.add_argument('--output', '-o', action='store', default="output/out.csv")
args = cli.parse_args()

logger = logging.getLogger('UGPS')
handler = logging.FileHandler('ugps.log')
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
