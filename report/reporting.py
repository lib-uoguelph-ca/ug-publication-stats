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
    This class determines the external interface that each report must define.
    Every report must inherit from this class.
    """

    # Determines the human readable name that will display in the report list, and the file name used when exporting.
    name = ""

    # Just extra information describing the report itself.
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
        """
        The get_values function iterates through self.mapping.
        Each key in the mapping defines a column in the resultant CSV.

        The value of the mapping can be:
        * A string. Treat the record as a dict and try to fetch the attribute name listed in the string
        * A callable. Call the function, passing in the record as a parameter.
        * None. Add the column to the result set, but leave it blank.

        :param record:
        :return:
        """
        result = {}
        for key, val in self.mapping.items():
            result[key] = self.get_value(record, key)
        return result

    def get_value(self, record, key):
        """
        Get a single value defined in self.mapping.

        :param record: The record to get the value from.
        :param key: The key to find in self.mapping.
        :return: String, the value or None if the value can't be found.
        """
        if isinstance(self.mapping[key], str):
            return getattr(record,self.mapping[key])
        elif callable(self.mapping[key]):
            return self.mapping[key](record)
        elif self.mapping[key] is None:
            return ''
        else:
            return ''

    def make_file_name(self):
        """
        Using the class' name attribute, generate a file name suitable for most filesystems.
        :return: String, the file name.
        """
        import re
        file_name = re.sub('[^\w\d-]', '-', self.name)
        return file_name

