from abc import ABC, abstractmethod


class Reporter:
    """
    A class to manage and run reports
    """

    def __init__(self, outfile):
        self.reports = {}
        self.outfile = outfile


    def list(self):
        """
        Returns a list of available reports, suitable for printing.
        """
        results = [cls.as_string() for name, cls in self.reports.items()]
        return results

    def all(self):
        """
        Run all currently registered reports.
        """
        for name, cls in self.reports.items():
            report = cls()
            report.run(self.outfile)

    def report(self, report):
        """
        Run a single report
        :param report: A string representing the name of the report to run.
        """
        if report in self.reports:
            r = self.reports[report]()
            r.run(self.outfile)

    def register(self, report):
        """
        Register a report class in the report manager.
        :param report: The class to register.
        The class must implement the interface defined in the Report class.
        """
        if issubclass(report, Report):
            self.reports[report.name] = report

    def register_all(self):
        """
        Register all report subclasses automatically.
        """
        for c in Report.__subclasses__():
            self.register(c)


class Report(ABC):
    """
    Abstract base class for encapsulating a report.
    Every report must inherit from this class.
    """

    name = ""
    description = ""

    mapping = {}

    def __str__(self):
        return f"{self.name}: {self.description}"

    @classmethod
    def as_string(cls):
        return f"{cls.name}: {cls.description}"

    @abstractmethod
    def run(self, outfile = None):
        pass

    def get_values(self, record):
        result = {}
        for key, val in self.mapping.items():
            result[key] = self.get_value(record, key)
        return result

    def get_value(self, record, key):
        if isinstance(self.mapping[key], str):
            return getattr(record,self.mapping[key])
        elif callable(self.mapping[key]):
            return self.mapping[key](record)
        elif self.mapping[key] is None:
            return ''
        else:
            return ''

    def _make_file_name(self):
        import re
        file_name = re.sub('[^\w\d-]', '-', self.name)
        return file_name

