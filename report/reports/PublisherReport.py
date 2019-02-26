from report.reporting import Report
from models import db_file_name

from csv import DictWriter
import sqlite3


class PublisherReport(Report):

    name = "Publisher Report"
    description = "OA article counts by publisher"

    mapping = {
        'publisher': lambda record: record['name'],
        'oa count': lambda record: record['oa_count'],
        'hybrid count': lambda record: record['hybrid_count'],
        'bronze count': lambda record: record['bronze_count'],
        'green count': lambda record: record['green_count'],
    }

    def __init__(self):
        self.conn = sqlite3.connect(db_file_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.mapping['estimated apc cost'] = self.estimate_cost

    def __del__(self):
        self.conn.close()

    def do_query(self):

        results = self.cursor.execute(
            """
            SELECT p.name as name, 
                sum(a.oa) as oa_count, 
                sum(a.hybrid) as hybrid_count, 
                sum(a.bronze) as bronze_count, 
                sum(a.self_archived) as green_count,
                p.average_apc as average_apc
            FROM article a 
            LEFT JOIN publisher p on a.publisher_id = p.id
            GROUP BY a.publisher_id
            """)

        return results.fetchall()

    def run(self, outfile=None):

        print(f"Running {self.name}")

        if not outfile:
            file_name = self._make_file_name()
            outfile = f'./output/{file_name}.csv'

        with open(outfile, 'w', newline='') as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.mapping.keys())
            writer.writeheader()

            results = self.do_query()

            for result in results:
                writer.writerow(self.get_values(result))

    def estimate_cost(self, record):

        if record['average_apc']:
            record_count = record['oa_count'] + record['hybrid_count']
            estimated_cost = record_count * record['average_apc']
            return estimated_cost

        return None
