from peewee import *

db_file_name = 'ugps.db'
db = SqliteDatabase(db_file_name)


class BaseModel(Model):
    class Meta:
        database = db


class Author(BaseModel):
    first_name = CharField(null=True)
    last_name = CharField()
    orcid = CharField(null=True)
    affiliation = CharField(null=True)
    local = BooleanField(default=False)
    college = CharField(null=True)
    department = CharField(null=True)


class Publisher(BaseModel):
    name = CharField()
    average_apc = FloatField(null=True)


class Journal(BaseModel):
    name = CharField()
    average_apc = FloatField(null=True)

class JournalIdentifier(BaseModel):
    journal = ForeignKeyField(Journal, backref='identifiers')
    type = CharField()
    identifier = CharField()

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
    self_archived = BooleanField(null=True)
    self_archived_count = SmallIntegerField(null=True)
    doi = CharField(null=True)
    doi_url = CharField(null=True)
    citations = IntegerField(null=True, default=0)


class Authored(BaseModel):
    author = ForeignKeyField(Author, backref='articles')
    article = ForeignKeyField(Article, backref='authors')


class Location(BaseModel):
    article = ForeignKeyField(Article, backref='article')
    url = CharField(null=True)

