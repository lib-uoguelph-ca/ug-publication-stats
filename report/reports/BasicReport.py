from report.reporting import Report


class BasicReport(Report):
    """
    A basic stub report for testing.
    """

    name = "Basic Report"
    description = "Just the basics"

    def run(self):
        print("Running basic report")
