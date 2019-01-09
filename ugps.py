from wos import WosClient
import wos.utils
import logging

import secrets
from unpaywall import UnpaywallClient
from models import *


# with WosClient(secrets.WOS_USER, secrets.WOS_PASS) as client:
#     print(wos.utils.query(client, 'OG="University of Guelph"'))


def init_db():
    """
    Initialize the database, creating the tables if not already present

    :return: A peewee database object
    """
    from peewee import SqliteDatabase

    db = SqliteDatabase('ugps.db')
    with db:
        db.create_tables([Author, Publisher, Journal, Article, Authored])

    return db


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
dois = get_dois()

logger = logging.getLogger('UGPS')
logger.addHandler(logging.FileHandler('ugps.log'))
uc = UnpaywallClient('doana@uoguelph.ca', logger)

data = []
for doi in dois:
    record = uc.lookup(doi)
    if record:
        data.append(record)

print(data)
