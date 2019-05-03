from report.reporting import Report
from models import Article
from csv import DictWriter


class BasicReport(Report):

    name = "Basic OA Summary"
    description = "OA Articles flagged by OA status (Bronze, Hybrid, Green)."

    mapping = {
        'title': 'title',
        'publisher': lambda article: article.publisher.name,
        'journal': lambda article: article.journal.name,
        'year': 'year',
        'oa': 'oa',
        'hybrid': 'hybrid',
        'bronze': 'bronze',
        'self_archived': 'self_archived',
        'doi': 'doi',
        'doi_url': 'doi_url',
        'citations': 'citations',
        'apc': lambda article: article.journal.average_apc_usd
    }

    def run(self, outfile=None):

        print(f"Running {self.name}")

        file_name = self.make_file_name()
        if not outfile:
            outfile = f'./output/{file_name}.csv'
        else:
            outfile = f'{outfile}/{file_name}.csv'

        with open(outfile, 'w', newline='') as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.mapping.keys())
            writer.writeheader()

            articles = Article.select()
            for article in articles.iterator():
                writer.writerow(self.get_values(article))
