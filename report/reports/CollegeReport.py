from models import db_file_name
from report.reporting import Report

from csv import DictWriter
import sqlite3


class CollegeReport(Report):

    name = "College Report"
    description = "OA counts by college"

    mapping = {
        'college': lambda record: record['college'],
        'oa count': lambda record: record['oa_count'],
        'hybrid count': lambda record: record['hybrid_count'],
        'bronze count': lambda record: record['bronze_count'],
        'green count': lambda record: record['green_count'],
    }

    def __init__(self):
        conn = sqlite3.connect(db_file_name)
        conn.row_factory = sqlite3.Row

        self.conn = conn
        self.cursor = conn.cursor()

    def __del__(self):
        self.conn.close()

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

            results = self.cursor.execute(
                """
                SELECT u.college as college,
                sum(a.oa) as oa_count, 
                sum(a.hybrid) as hybrid_count, 
                sum(a.bronze) as bronze_count, 
                sum(a.self_archived) as green_count 
                FROM article a
                LEFT JOIN authored w on a.id = w.article_id
                LEFT JOIN author u on w.author_id = u.id
                GROUP BY u.college
                """
            ).fetchall()

            for result in results:
                writer.writerow(self.get_values(result))
