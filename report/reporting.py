from abc import ABC, abstractmethod


class Reporter:
    def __init__(self):
        self.reports = {}

    def list(self):
        results = [cls.as_string() for name, cls in self.reports.items()]
        return results


    def all(self):
        return "Run all reports"

    def report(self, report):
        pass

    def register(self, report):
        self.reports[report.name] = report

    def register_all(self):
        for c in Report.__subclasses__():
            self.register(c)


class Report(ABC):
    name = ""
    description = ""

    def __str__(self):
        return f"{self.name}: {self.description}"

    @classmethod
    def as_string(cls):
        return f"{cls.name}: {cls.description}"

    @abstractmethod
    def run(self):
        pass
