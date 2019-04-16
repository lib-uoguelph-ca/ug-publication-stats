from report.reporting import Report
from models import db_file_name

from csv import DictWriter
import sqlite3


class JournalReport(Report):

    name = "Repository Report"
    description = "Top repositories"

    mapping = {
        'domain': lambda record: record['domain'],
        'oa count': lambda record: record['oa_count'],
        'hybrid count': lambda record: record['hybrid_count'],
        'bronze count': lambda record: record['bronze_count'],
        'green count': lambda record: record['green_count'],
        'total count': lambda record: record['total_count'],
        'citations': lambda record: record['citations']
    }

    def __init__(self):
        conn = sqlite3.connect(db_file_name)
        conn.row_factory = sqlite3.Row

        self.conn = conn
        self.cursor = conn.cursor()

    def __del__(self):
        self.conn.close()

    def do_query(self):

        results = self.cursor.execute(
            """
            SELECT SUBSTR(
                REPLACE(REPLACE(url, 'https://', ''), 'http://', ''),0, INSTR(REPLACE(REPLACE(url, 'https://', ''), 'http://', ''), '/')) as domain,
                SUM(oa) as oa_count,
                SUM(hybrid) as hybrid_count,
                SUM(self_archived) as green_count,
                SUM(bronze) as bronze_count,
                COUNT(article.id) as total_count,
                SUM(citations) as citations
            FROM article INNER JOIN location on article.id = location.article_id GROUP BY domain;       
            """)

        return results.fetchall()

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

            results = self.do_query()

            for result in results:
                writer.writerow(self.get_values(result))