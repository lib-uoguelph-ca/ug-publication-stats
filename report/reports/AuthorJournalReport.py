from models import Author
from report.reporting import Report

from csv import DictWriter
from collections import Counter


class AuthorJournalReport(Report):

    name = "Author Journal Report"
    description = "What journals are authors publishing OA works in?"

    mapping = {
        'first name': 'first_name',
        'last name': 'last_name',
        'college': 'college',
        'department': 'department',
        'journals': None,
    }

    def __init__(self):
        self.mapping['journals'] = self._get_journals

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

            results = Author.select()

            for result in results:
                if result.local:
                    writer.writerow(self.get_values(result))

    def _get_journals(self, author):
        """
        Given an author record, return a string representing the list of jorunals that they have published in
        along with the number of times they have published in each.

        Note: Only counts Open access or hybrid publicaitons.
        :param author: An author record
        :return: A string representing the author's journal publication history.
        """
        journal_list = []
        for article in author.articles:
            if article.article.oa or article.article.hybrid:
                journal_list.append(article.article.journal.name)

        journals = Counter(journal_list)
        journal_string = '; '.join([f"{journal} ({count})" for journal, count in journals.items()])

        return journal_string
