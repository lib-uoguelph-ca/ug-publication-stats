from models import *
import datetime


def persist(record):
    create_authors(record)
    create_article(record)
    associate_authors(record)


def create_authors(record):
    authors = record['z_authors']

    authors = []
    for author in authors:
        result = Author.get_or_create(first_name=author['given'], last_name=author['family'])
        authors.append(result[0])

    return authors


def create_publisher(record):
    result = Publisher.get_or_create(name=record['publisher'])
    return result[0]

def create_journal(record):
    result = Journal.get_or_create(name=record['publisher'])
    return result[0]

def create_article(record):
    journal = create_journal(record)
    publisher = create_publisher(record)

    date_str = record['published_date']
    pub_date = None

    if date_str:
        pub_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

    result = Article.get_or_create(
        title=record['title'],
        year=pub_date.year,
        journal=journal,
        publisher=publisher,
        oa = record['is_oa'],
        hybrid = None,
        bronze = None,
        self_archived = None,
        url=record['doi_url']
    )

    return result

def associate_authors(record):
    pass

