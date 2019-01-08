from peewee import *

db = SqliteDatabase('ugps.db')

class BaseModel(Model):
    class Meta:
        database = db


class Author(BaseModel):
    first_name = CharField()
    last_name = CharField()
    affiliation = CharField()


class Publisher(BaseModel):
    name = CharField()


class Journal(BaseModel):
    name = CharField()


class Article(BaseModel):
    title = CharField()
    publisher = ForeignKeyField(Publisher, backref='articles')
    journal = ForeignKeyField(Journal, backref='articles')
    year = SmallIntegerField()
    oa = BooleanField()
    hybrid = BooleanField()
    bronze = BooleanField()
    self_archived = SmallIntegerField()
    url = CharField()

class Authored(BaseModel):
    author = ForeignKeyField(Author, backref='articles')
    article = ForeignKeyField(Article, backref='authors')

