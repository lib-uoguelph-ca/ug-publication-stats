

from ldap3 import Server, Connection
import logging

class LDAPClient:

    def __init__(self, endpoint, port, basedn, user=None, password=None):
        server = Server(host=endpoint, port=port, use_ssl=True)

        if user and password:
            self.conn = Connection(server, user=f"{user},{basedn}", password=password, read_only=True)
        else:
            self.conn = Connection(server, read_only=True)

        self.conn.bind()
        self.basedn = basedn

    def __del__(self):
        self.conn.unbind()

    def get_department(self, first_name, last_name):
        filter = f"(cn={first_name} {last_name})"
        self.conn.search(search_base=self.basedn, search_filter=filter, attributes=['ou'])

        if len(self.conn.response) == 1:
            entry = self.conn.entries[0]
            return str(entry['ou'])

        return None


