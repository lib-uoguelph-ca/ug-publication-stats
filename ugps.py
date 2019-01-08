from wos import WosClient
import wos.utils

import secrets

# with WosClient(secrets.WOS_USER, secrets.WOS_PASS) as client:
#     print(wos.utils.query(client, 'OG="University of Guelph"'))

from models import *


def init_db():
    from peewee import SqliteDatabase

    db = SqliteDatabase('ugps.db')
    with db:
        db.create_tables([Author, Publisher, Journal, Article, Authored])
    return db


init_db()
