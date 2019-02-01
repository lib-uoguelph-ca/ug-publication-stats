from models import *


def init_db():
    """
    Initialize the database, creating the tables if not already present

    :return: A peewee database object
    """
    from peewee import SqliteDatabase

    db = SqliteDatabase('ugps.db')
    with db:
        db.create_tables([Author, Publisher, Journal, Article, Authored, Published])

    return db


def clean_db():
    Author.delete().execute()
    Publisher.delete().execute()
    Journal.delete().execute()
    Authored.delete().execute()
    Article.delete().execute()


def persist(record):
    create_authors(record)
    create_article(record)
    associate_authors(record)


def create_authors(record):
    authors = record.get_authors()

    author_list = []
    for author in authors:
        result = Author.get_or_create(first_name=author['given'], last_name=author['family'])
        author_list.append(result[0])

    return authors


def create_publisher(record):
    result = Publisher.get_or_create(name=record.get_publisher())
    return result[0]


def create_journal(record):
    result = Journal.get_or_create(name=record.get_journal_title())
    return result[0]


def create_article(record):
    journal = create_journal(record)
    publisher = create_publisher(record)



    result = Article.get_or_create(
        title=record.get_title(),
        year=record.get_year(),
        journal=journal,
        publisher=publisher,
        oa = record.is_oa(),
        hybrid = record.is_hybrid(),
        bronze = record.is_bronze(),
        self_archived = record.get_self_archived(),
        doi_url=record.get_doi()
    )

    return result


def associate_authors(record):
    pass

