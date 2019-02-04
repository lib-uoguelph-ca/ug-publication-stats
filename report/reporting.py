from abc import ABC, abstractmethod


class Reporter:
    """
    A class to manage and run reports
    """

    def __init__(self):
        self.reports = {}

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
            report.run()

    def report(self, report):
        """
        Run a single report
        :param report: A string representing the name of the report to run.
        """
        if report in self.reports:
            r = self.reports[report]()
            r.run()

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

    def __str__(self):
        return f"{self.name}: {self.description}"

    @classmethod
    def as_string(cls):
        return f"{cls.name}: {cls.description}"

    @abstractmethod
    def run(self):
        pass
