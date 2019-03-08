from storage.record import BaseArticleRecord, BaseAuthorRecord

import urllib.parse
import requests
import threading
import queue


class UnpaywallClient:

    def __init__(self, email, logger=None):
        self.logger = logger
        self.email = email
        self.endpoint = 'https://api.unpaywall.org/v2/'

    def lookup(self, doi):
        """
        Fetch info on a single DOI fromt the API.
        :param doi: The doi to query
        :return: Response data or None
        """
        self.logger.debug(f"Unpaywall: Fetching DOI: {doi}")

        try:
            request_url = self.endpoint + urllib.parse.quote(doi) + "?email=" + self.email
            response = requests.get(request_url)
            response.raise_for_status()  # Throw exceptions for bad requests

        except requests.exceptions.HTTPError as error:
            if self.logger:
                self.logger.error(f"Unpaywall request error for doi: {doi} - {error}")

            return None
        except TypeError as error:
            if self.logger:
                self.logger.error(f"Can't escape DOI: {doi} - {error}")
            return None

        data = response.json()
        return data

    def fetchall(self, dois):
        for doi in dois:
            yield self.lookup(doi)


class UnpaywallArticleRecord(BaseArticleRecord):

    def __init__(self, record):
        self.hybrid = False
        self.bronze = False
        self.green = 0

        self.preprocess(record)

    def preprocess(self, record):

        self.metadata['title'] = record['title']
        self.metadata['date'] = record['published_date']
        self.metadata['year'] = record['year']
        self.metadata['journal'] = record['journal_name']
        self.metadata['type'] = record['genre']
        self.metadata['publisher'] = record['publisher']
        self.metadata['oa'] = record['is_oa']
        self.metadata['doi'] = record['doi']
        self.metadata['doi_url'] = record['doi_url']
        self.metadata['locations'] = record['oa_locations']
        self.metadata['authors'] = self._get_authors(record)

        self._set_flags(record)

        self.metadata['hybrid'] = self.hybrid
        self.metadata['bronze'] = self.bronze
        self.metadata['self_archived'] = self.green > 0
        self.metadata['self_archived_count'] = self.green

    def _set_flags(self, record):
        """
        Scan through the record and:
        - Set various flags relating to the style of OA.
        - Count how many green OA locations there are

        This way we don't have to do this every time we want to look up this information.
        """
        if not self.is_oa():
            return

        locations = self.get_locations()

        # If the record is in DOAJ or flagged as OA it's gold
        gold = False
        if record['journal_is_in_doaj'] or record['journal_is_oa']:
            gold = True

        for loc in locations:
            # If it has a location that is of type 'repository' it's green
            if loc['host_type'] == 'repository':
                self.green += 1

            # If the host is a publisher and it has no license, it's bronze
            # If it has a license that's not a creative commons license, it's bronze
            # If it has a creative commons license, it's hybrid.
            if not gold and loc['host_type'] == 'publisher':
                if not loc['license']:
                    self.bronze = True

                if loc['license'] and loc['license'][0:2] == 'cc':
                    self.hybrid = True
                else:
                    self.bronze = True

    def _get_authors(self, record):
        if not record['z_authors']:
            return []

        authors = [UnpaywallAuthor(author) for author in record['z_authors']]
        return authors


class UnpaywallAuthor(BaseAuthorRecord):
    def __init__(self, author):
        self.record = author
        self.metadata['first_name'] = self._get_optional_value(author, 'given')
        self.metadata['last_name'] = self._get_optional_value(author, 'family')
        self.metadata['orcid'] = self._get_optional_value(author, 'ORCID')
        self.metadata['affiliations'] = self._get_affiliations(author)

    def _get_affiliations(self, author):
        values = self._get_optional_value(author, 'affiliation')

        if not values:
            return None

        results = [value['name'] for value in values]

        return '; '.join(results)

    def _get_optional_value(self, record, key):
        if key in record:
            return record[key]

        return None


class UnpaywallThread(threading.Thread):

    def __init__(self, id, queue, email, results, logger=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.id = id
        self.logger = logger
        self.results = results
        self.client = UnpaywallClient(email, self.logger)
        # Essentially a synchronized flag that's set when the thread is asked to stop (join)
        self.stoprequest = threading.Event()

    def run(self):
        while not self.stoprequest.is_set():
            try:
                item = self.queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                result = self._do_request(item)
                if result:
                    self.results.append(result)
            except requests.exceptions.RequestException:
                self.logger.warn(f"Request failed: {item}")
                continue

            # send a signal to the queue that the job is done
            self.queue.task_done()

    """
    Public method to signal that the thread has been asked to stop
    """

    def stop(self):
        self.stoprequest.set()

    def _do_request(self, item):
        self.logger.debug(f"Thread {self.id}: Query {item}")
        return self.client.lookup(item)


class ThreadedUnpaywallClient:
    def __init__(self, results, email, num_threads=3, thread_class=UnpaywallThread, logger=None):
        self.queue = queue.Queue()
        self.num_threads = num_threads
        self.threads = []
        self.thread_class = thread_class
        self.logger = logger
        self.results = results
        self.email = email
        self._init_threads()

    def get_queue(self):
        return self.queue

    def _init_threads(self):
        for i in range(self.num_threads):
            thread = self.thread_class(i, self.queue, self.email, self.results, self.logger)
            self.threads.append(thread)
            thread.start()

    def stop(self):
        self.queue.join()  # Blocks until all unfinished items have been processed.
        self._cleanup()

    def _cleanup(self):
        for thread in self.threads:
            thread.stop()
