from doaj import DOAJClient
import openapc
from models import Journal, JournalIdentifier, Publisher
from currency_converter import CurrencyConverter
from datetime import date
from time import sleep


class APCUpdater:
    def __init__(self, logger):
        self.logger = logger

        self.doaj = DOAJClient(logger)

        # Use OpenAPC to endpoint to fetch average APC costs for each publisher
        self.oapc = openapc.OpenAPC()

        self.exchange = Exchange()

    def update(self):
        # self.oapc.update_publisher_data()
        self.update_journals()
        self.update_publishers()

    def update_journals(self):
        """
        Update APC information for journals

        The strategy here is to update first from DOAJ, then fill in the blanks from OpenAPC.
        :return:
        """

        # DOAJ Update
        for journal in Journal.select():
            apcs = self.journal_get_apcs(journal)
            self.journal_update(journal, apcs)

        # OpenAPC update
        oapc_journal_data = self.oapc.get_journal_data()
        for row in oapc_journal_data:
            journal = Journal.get_or_none(name=row['journal_full_title'])
            self.logger.debug(f"Open APC Journal Lookup - {row['journal_full_title']}")
            if journal:
                self.logger.debug("Matched Journal")
                if journal.average_apc is not None:
                    journal.average_apc = row['apc_amount_avg']
                    journal.average_apc_unit = 'EUR'
                    journal.average_apc_usd = self.exchange.convert_now(row['apc_amount_avg'], 'EUR')
                    journal.save()

    def update_publishers(self):
        data = self.oapc.get_publisher_data()

        for row in data:
            publisher = Publisher.get_or_none(name=row['publisher'])
            self.logger.debug(f"Open APC Publisher Lookup - {row['publisher']}")
            if publisher:
                self.logger.debug("Matched Publisher")
                publisher.average_apc = row['apc_amount_avg']
                publisher.average_apc_unit = 'EUR'
                publisher.average_apc_usd = self.exchange.convert_now(row['apc_amount_avg'], 'EUR')
                publisher.save()

    def journal_update(self, journal, apcs):
        try:
            journal.average_apc = sum(apcs['values']) / len(apcs['values'])
            journal.average_apc_unit = apcs['unit']
            journal.average_apc_usd = sum(apcs['usd_values']) / len(apcs['usd_values'])
            self.logger.debug(f"DOAJ APC Journal update - {journal.name}")
            journal.save()
        except (KeyError, TypeError):
            return

    def journal_get_apcs(self, journal):
        """
        The issue here is that a single journal might have several ISSNs, and DOAJ might have an APC for each ISSN
        When this happens, we're storing the average.

        :param journal:
        :return: A dict containing the unit, the values in that local unit, and the values converted to USD.
        """

        apcs = {
            'unit': '',
            'values': [],
            'usd_values': []
        }

        for identifier in journal.identifiers:
            if identifier.type == "issn":
                data = self.doaj.get_journal_by_issn(identifier.identifier)
                sleep(1)

            if data is not None:
                try:
                    oa_start_year = data['bibjson']['oa_start']['year']
                    apc_unit = data['bibjson']['apc']['currency']

                    apcs['unit'] = apc_unit

                    apc = data['bibjson']['apc']['average_price']
                    apcs['values'].append(apc)

                    if apc_unit != "USD":
                        apc_usd = self.exchange.convert_range(apc, apc_unit, 'USD', oa_start_year)
                    else:
                        apc_usd = apc

                    apcs['usd_values'].append(apc_usd)

                    return apcs

                except KeyError:
                    continue


class Exchange:
    def __init__(self):
        # Use Currency converter to convert foreign currencies to USD
        self.exchange = CurrencyConverter(fallback_on_missing_rate=True)

    def convert_now(self, value, currency, to_currency='USD'):
        return self.exchange.convert(value, currency, to_currency)

    # TODO: Move this somewhere else so other classes can use it easily.
    def convert_range(self, value, currency, to_currency='USD',  year=None):
        """
        :param value: The currency value
        :param currency: Three letter currency code indicating the current currency
        :param to_currency: The currency to convert to
        :param year: The year that the journal started publishing
        :return The value in USD
        :rtype: float
        """

        if year is None:
            year = date.today().year

        current_year = date.today().year
        years = [y for y in range(year, current_year + 1)]
        values = [self.exchange.convert(value, currency, to_currency, date=date(y, 1, 1)) for y in years]
        avg = sum(values) / len(values)
        return avg
