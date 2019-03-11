from models import *
from peewee import IntegrityError


class DB:
    def __init__(self, logger):
        self.logger = logger

    def init_db(self):
        """
        Initialize the database, creating the tables if not already present

        :return: A peewee database object
        """
        from peewee import SqliteDatabase

        self.logger.debug('No database file found - Creating database')

        db = SqliteDatabase('ugps.db')
        with db:
            db.create_tables([Author, Publisher, Journal, Article, Authored, Location])

        return db

    def clean_db(self):
        """
        Remove all rows from all tables.
        """

        self.logger.debug('Cleaning database')

        Author.delete().execute()
        Publisher.delete().execute()
        Journal.delete().execute()
        Authored.delete().execute()
        Article.delete().execute()

    def persist(self, record):
        """
        Save a record to the database.
        :param record: BaseArticleRecord
        """

        authors = self.create_authors(record)
        article = self.create_article(record)
        if article:
            self.associate_authors(article, authors)
            self.create_locations(record, article)

    def create_authors(self, record):
        """
        Create (or find) authors for a given record.
        :param record: BaseArticleRecord
        :return: a list of Author models
        """
        authors = record.get_authors()

        author_list = []
        for author in authors:
            try:
                result = Author.get_or_create(
                    first_name=author.get_first_name(),
                    last_name=author.get_last_name(),
                    orcid=author.get_orcid(),
                    affiliation=author.get_affiliations()
                )

                author_list.append(result[0])
            except IntegrityError:
                self.logger.error(f'Author integrity constraint failed for DOI: {record.get_doi()}')
                continue

        return author_list

    def create_publisher(self, record):
        """
        Create (or get if it already exists) a publisher for the given record
        :param record: BaseArticleRecord
        :return: A Publisher model
        """
        try:
            result = result = Publisher.get_or_create(name=record.get_publisher())
            return result[0]
        except IntegrityError:
            self.logger.error(f'Publisher integrity constraint failed for DOI: {record.get_doi()}')
            return None

    def create_journal(self, record):
        """
        Create (or get if it already exists) a journal for the given record
        :param record: BaseArticleRecord
        :return: A Journal model
        """
        try:
            result = Journal.get_or_create(name=record.get_journal_title())
            return result[0]
        except IntegrityError:
            self.logger.error(f'Journal integrity constraint failed for DOI: {record.get_doi()}')
            return None

    def create_article(self, record):
        """
        Create an article record for the given record
        :param record: BaseArticleRecord
        :return: An Article model
        """
        journal = self.create_journal(record)
        publisher = self.create_publisher(record)

        try:
            result = Article.get_or_create(
                title=record.get_title(),
                type=record.get_type(),
                date=record.get_date(),
                year=record.get_year(),
                journal=journal,
                publisher=publisher,
                oa=record.is_oa(),
                hybrid=record.is_hybrid(),
                bronze=record.is_bronze(),
                self_archived=record.get_self_archived(),
                self_archived_count=record.get_self_archived_count(),
                doi=record.get_doi(),
                doi_url=record.get_doi_url(),
                citations=record.get_citations()
            )

            return result[0]

        except IntegrityError:
            self.logger.error(f'Journal integrity constraint failed for DOI: {record.get_doi()}')
            return None

    def associate_authors(self, article, authors):
        """
        Create the links between an article and its authors
        :param article: The article model
        :param authors: A list of author models
        """
        for author in authors:
            try:
                Authored.get_or_create(author=author, article=article)
            except IntegrityError:
                self.logger.error(f'Author-Article integrity constraint failed for Article: {article.id}, Author: {author.id}')

    def create_locations(self, record, article):
        """
        Given a record, record the locations of all copies of the article.
        :param record: BaseArticleRecord
        :param article: The Article model
        :return:
        """
        locations = record.get_locations()

        # TODO: Locations should be implemented as some sort of value object,
        #       to prevent the Unpaywall API implementation from leaking into this class.
        for location in locations:
            try:
                Location.get_or_create(article=article, url=location['url'])
            except IntegrityError:
                self.logger.error(f'Location integrity constraint failed for Article: {article.id}, Location: {location["url"]}')
