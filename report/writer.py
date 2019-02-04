from abc import ABC, abstractmethod


class Writer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def export(self, data):
        pass


class CSVReportWriter(Writer):

    def __init__(self, outfile):
        self.outfile = outfile

    def export(self, data):
        pass

