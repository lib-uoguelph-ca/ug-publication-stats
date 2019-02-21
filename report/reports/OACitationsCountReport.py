from report.reporting import Report
from models import Article, db_file_name

import sqlite3
import pandas as pd

class OACitationsCountReport(Report):

    name = "OA Citation Count"
    description = "Count articles by OA status and citations"


    def run(self, outfile=None):
        print(f"Running {self.name}")
        self._all_years(outfile)
        self._by_year(outfile)

    def _by_year(self, outfile):
        years = self._get_years()

        for year in years:

            if not outfile:
                file_name = self._make_file_name()
                file_name = f'./output/{file_name}-{year}.csv'
            else:
                file_name = f"{outfile}-{year}.csv"

            self._do_year(year, file_name)

    def _get_years(self):
        conn = sqlite3.connect(db_file_name)
        c = conn.cursor()

        results = c.execute("SELECT DISTINCT year FROM article").fetchall()
        years = [result[0] for result in results]
        years.sort()
        return years

    def _do_year(self, year, outfile):
        conn = sqlite3.connect(db_file_name)
        c = conn.cursor()

        results = pd.DataFrame(index=[
            "Just Gold",
            "Just Hybrid",
            "Just Bronze",
            "Just Green",
            "Gold + Green",
            "Hybrid + Green",
            "Bronze + Green",
            "More Than One Green",
            "All Green",
            "All Open",
            "All Closed",
            "Total"
        ],
        columns=[
            "Articles",
            "Citations",
            "Average Citations Per Article"
        ])

        num_articles = Article.select().where(Article.year == year).count()

        gold_count = Article.select().where(
            Article.oa == True,
            Article.hybrid == False,
            Article.bronze == False,
            Article.self_archived == 0,
            Article.year == year
        ).count()
        results.loc["Just Gold", "Articles"] = gold_count

        hybrid_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == True,
            Article.bronze == False,
            Article.self_archived == 0,
            Article.year == year
        ).count()
        results.loc["Just Hybrid", "Articles"] = hybrid_count

        bronze_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == False,
            Article.bronze == True,
            Article.self_archived == 0,
            Article.year == year
        ).count()
        results.loc["Just Bronze", "Articles"] = bronze_count

        green_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == False,
            Article.bronze == False,
            Article.self_archived > 0,
            Article.year == year
        ).count()
        results.loc["Just Green", "Articles"] = green_count

        gold_green_count = Article.select().where(
            Article.oa == True,
            Article.hybrid == False,
            Article.bronze == False,
            Article.self_archived > 0,
            Article.year == year
        ).count()
        results.loc["Gold + Green", "Articles"] = gold_green_count

        hybrid_green_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == True,
            Article.bronze == False,
            Article.self_archived > 0,
            Article.year == year
        ).count()
        results.loc["Hybrid + Green", "Articles"] = hybrid_green_count

        bronze_green_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == False,
            Article.bronze == True,
            Article.self_archived > 0,
            Article.year == year
        ).count()
        results.loc["Bronze + Green", "Articles"] = bronze_green_count

        more_than_one_green_count = Article.select().where(
            Article.self_archived > 1,
            Article.year == year
        ).count()
        results.loc["More Than One Green", "Articles"] = more_than_one_green_count

        all_green_count = Article.select().where(
            Article.self_archived > 0,
            Article.year == year
        ).count()
        results.loc["All Green", "Articles"] = all_green_count

        all_open_count = gold_count + hybrid_count + bronze_count + green_count + gold_green_count + hybrid_green_count + bronze_green_count
        results.loc["All Open", "Articles"] = all_open_count

        all_closed_count = num_articles - all_open_count
        results.loc["All Closed", "Articles"] = all_closed_count

        results.loc["Total", "Articles"] = num_articles

        num_citations = c.execute(f"SELECT SUM(article.citations) FROM article WHERE year={year}").fetchone()[0]

        gold_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa = 1 
            AND hybrid = 0 
            AND bronze = 0 
            AND self_archived = 0
            AND year = ?""", (year,)).fetchone()[0]

        gold_citations = self._val_or_zero(gold_citations)
        results.loc["Just Gold", "Citations"] = gold_citations

        hybrid_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa = 0 
            AND hybrid = 1 
            AND bronze = 0 
            AND self_archived = 0
            AND year = ?""", (year, )).fetchone()[0]

        hybrid_citations = self._val_or_zero(hybrid_citations)
        results.loc["Just Hybrid", "Citations"] = hybrid_citations

        bronze_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa = 0 
            AND hybrid = 0 
            AND bronze = 1 
            AND self_archived = 0
            AND year = ?""", (year,)).fetchone()[0]

        bronze_citations = self._val_or_zero(bronze_citations)
        results.loc["Just Bronze", "Citations"] = bronze_citations

        green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  0
            AND hybrid = 0 
            AND bronze = 0 
            AND self_archived > 0
            AND year = ?""", (year,)).fetchone()[0]

        green_citations = self._val_or_zero(green_citations)
        results.loc["Just Green", "Citations"] = green_citations

        gold_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  1
            AND hybrid = 0 
            AND bronze = 0 
            AND self_archived > 0
            AND year = ?""", (year,)).fetchone()[0]

        gold_green_citations = self._val_or_zero(gold_green_citations)
        results.loc["Gold + Green", "Citations"] = gold_green_citations

        hybrid_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  0
            AND hybrid = 1 
            AND bronze = 0 
            AND self_archived > 0
            AND year = ?""", (year,)).fetchone()[0]

        hybrid_green_citations = self._val_or_zero(hybrid_green_citations)
        results.loc["Hybrid + Green", "Citations"] = hybrid_green_citations

        bronze_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  0
            AND hybrid = 0 
            AND bronze = 1 
            AND self_archived > 0
            AND year = ?""", (year,)).fetchone()[0]

        bronze_green_citations = self._val_or_zero(bronze_green_citations)
        results.loc["Bronze + Green", "Citations"] = bronze_green_citations

        more_than_one_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE self_archived > 1
            AND year = ?""", (year,)).fetchone()[0]

        more_than_one_green_citations = self._val_or_zero(more_than_one_green_citations)
        results.loc["More Than One Green", "Citations"] = more_than_one_green_citations

        all_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE self_archived > 0
            AND year = ?""", (year,)).fetchone()[0]

        all_green_citations = self._val_or_zero(all_green_citations)
        results.loc["All Green", "Citations"] = all_green_citations

        all_open_citations = gold_citations + hybrid_citations + bronze_citations + green_citations + gold_green_citations + hybrid_green_citations + bronze_green_citations
        results.loc["All Open", "Citations"] = all_open_citations

        all_closed_citations = num_citations - all_open_citations
        results.loc["All Closed", "Citations"] = all_closed_citations

        results.loc["Total", "Citations"] = num_citations

        conn.close()

        for index, row in results.iterrows():
            if row["Articles"] != 0:
                results["Average Citations Per Article"][index] = row["Citations"] / row["Articles"]
            else:
                results["Average Citations Per Article"][index] = 0

        results.to_csv(outfile)

    def _all_years(self, outfile):

        conn = sqlite3.connect(db_file_name)
        c = conn.cursor()

        results = pd.DataFrame(index=[
            "Just Gold",
            "Just Hybrid",
            "Just Bronze",
            "Just Green",
            "Gold + Green",
            "Hybrid + Green",
            "Bronze + Green",
            "More Than One Green",
            "All Green",
            "All Open",
            "All Closed",
            "Total"
        ],
        columns=[
            "Articles",
            "Citations",
            "Average Citations Per Article"
        ])


        if not outfile:
            file_name = self._make_file_name()
            outfile = f'./output/{file_name}.csv'

        num_articles = Article.select().count()

        gold_count = Article.select().where(
            Article.oa == True,
            Article.hybrid == False,
            Article.bronze == False,
            Article.self_archived == 0
        ).count()
        results.loc["Just Gold", "Articles"] = gold_count

        hybrid_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == True,
            Article.bronze == False,
            Article.self_archived == 0
        ).count()
        results.loc["Just Hybrid", "Articles"] = hybrid_count

        bronze_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == False,
            Article.bronze == True,
            Article.self_archived == 0
        ).count()
        results.loc["Just Bronze", "Articles"] = bronze_count

        green_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == False,
            Article.bronze == False,
            Article.self_archived > 0
        ).count()
        results.loc["Just Green", "Articles"] = green_count

        gold_green_count = Article.select().where(
            Article.oa == True,
            Article.hybrid == False,
            Article.bronze == False,
            Article.self_archived > 0
        ).count()
        results.loc["Gold + Green", "Articles"] = gold_green_count

        hybrid_green_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == True,
            Article.bronze == False,
            Article.self_archived > 0
        ).count()
        results.loc["Hybrid + Green", "Articles"] = hybrid_green_count

        bronze_green_count = Article.select().where(
            Article.oa == False,
            Article.hybrid == False,
            Article.bronze == True,
            Article.self_archived > 0
        ).count()
        results.loc["Bronze + Green", "Articles"] = bronze_green_count

        more_than_one_green_count = Article.select().where(
            Article.self_archived > 1
        ).count()
        results.loc["More Than One Green", "Articles"] = more_than_one_green_count

        all_green_count = Article.select().where(
            Article.self_archived > 0
        ).count()
        results.loc["All Green", "Articles"] = all_green_count

        all_open_count = gold_count + hybrid_count + bronze_count + green_count + gold_green_count + hybrid_green_count + bronze_green_count
        results.loc["All Open", "Articles"] = all_open_count

        all_closed_count = num_articles - all_open_count
        results.loc["All Closed", "Articles"] = all_closed_count

        results.loc["Total", "Articles"] = num_articles

        num_citations = c.execute("SELECT SUM(article.citations) FROM article").fetchone()[0]

        gold_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa = 1 
            AND hybrid = 0 
            AND bronze = 0 
            AND self_archived = 0"""
        ).fetchone()[0]
        gold_citations = self._val_or_zero(gold_citations)
        results.loc["Just Gold", "Citations"] = gold_citations

        hybrid_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa = 0 
            AND hybrid = 1 
            AND bronze = 0 
            AND self_archived = 0"""
        ).fetchone()[0]
        hybrid_citations = self._val_or_zero(hybrid_citations)
        results.loc["Just Hybrid", "Citations"] = hybrid_citations

        bronze_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa = 0 
            AND hybrid = 0 
            AND bronze = 1 
            AND self_archived = 0"""
        ).fetchone()[0]
        bronze_citations = self._val_or_zero(bronze_citations)
        results.loc["Just Bronze", "Citations"] = bronze_citations

        green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  0
            AND hybrid = 0 
            AND bronze = 0 
            AND self_archived > 0"""
        ).fetchone()[0]
        green_citations = self._val_or_zero(green_citations)
        results.loc["Just Green", "Citations"] = green_citations

        gold_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  1
            AND hybrid = 0 
            AND bronze = 0 
            AND self_archived > 0"""
        ).fetchone()[0]
        gold_green_citations = self._val_or_zero(gold_green_citations)
        results.loc["Gold + Green", "Citations"] = gold_green_citations

        hybrid_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  0
            AND hybrid = 1 
            AND bronze = 0 
            AND self_archived > 0"""
        ).fetchone()[0]
        hybrid_green_citations = self._val_or_zero(hybrid_green_citations)
        results.loc["Hybrid + Green", "Citations"] = hybrid_green_citations

        bronze_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE oa =  0
            AND hybrid = 0 
            AND bronze = 1 
            AND self_archived > 0"""
        ).fetchone()[0]
        bronze_green_citations = self._val_or_zero(bronze_green_citations)
        results.loc["Bronze + Green", "Citations"] = bronze_green_citations

        more_than_one_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE self_archived > 1"""
        ).fetchone()[0]
        more_than_one_green_citations = self._val_or_zero(more_than_one_green_citations)
        results.loc["More Than One Green", "Citations"] = more_than_one_green_citations

        all_green_citations = c.execute(
            """SELECT SUM(article.citations) FROM article 
            WHERE self_archived > 0"""
        ).fetchone()[0]
        all_green_citations = self._val_or_zero(all_green_citations)
        results.loc["All Green", "Citations"] = all_green_citations

        all_open_citations = gold_citations + hybrid_citations + bronze_citations + green_citations + gold_green_citations + hybrid_green_citations + bronze_green_citations
        results.loc["All Open", "Citations"] = all_open_citations

        all_closed_citations = num_citations - all_open_citations
        results.loc["All Closed", "Citations"] = all_closed_citations

        results.loc["Total", "Citations"] = num_citations

        conn.close()

        for index, row in results.iterrows():
            if row["Articles"] != 0:
                results["Average Citations Per Article"][index] = row["Citations"] / row["Articles"]
            else:
                results["Average Citations Per Article"][index] = 0

        results.to_csv(outfile)

    @staticmethod
    def _val_or_zero(value):
        if value is not None:
            return value
        else:
            return 0
