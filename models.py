from peewee import *

db = SqliteDatabase('ugps.db')

class BaseModel(Model):
    class Meta:
        database = db


class Author(BaseModel):
    first_name = CharField()
    last_name = CharField()
    orcid = CharField(null=True)
    affiliation = CharField(null=True)


class Publisher(BaseModel):
    name = CharField()


class Journal(BaseModel):
    name = CharField()


class Article(BaseModel):
    title = CharField()
    type = CharField(null=True)
    publisher = ForeignKeyField(Publisher, backref='articles')
    journal = ForeignKeyField(Journal, backref='articles')
    date = DateField(null=True)
    year = SmallIntegerField(null=True)
    oa = BooleanField(null=True)
    hybrid = BooleanField(null=True)
    bronze = BooleanField(null=True)
    self_archived = SmallIntegerField(null=True)
    doi = CharField(null=True)
    doi_url = CharField(null=True)

class Authored(BaseModel):
    author = ForeignKeyField(Author, backref='articles')
    article = ForeignKeyField(Article, backref='authors')

class Location(BaseModel):
    article = ForeignKeyField(Article, backref='article')
    url = CharField(null=True)

