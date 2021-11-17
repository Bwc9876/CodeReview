"""
    This file provides a fake ldap server to test with
"""
from typing import Optional
from uuid import uuid4

from django.conf import settings
from ldap3 import Connection, Server, MOCK_SYNC

from .ldap_auth import LDAPAuthentication


class LDAPMockAuthentication(LDAPAuthentication):
    """
        This class is a mock version of LDAPAuthentication meant for use in testing
        *NEVER* **EVER** USE THIS IN PRODUCTION
    """

    @classmethod
    def setup_server(cls):
        """
            This function constructs a fake server to connect to
        """

        if cls.server is None:
            cls.server = Server.from_definition('fake_server',
                                                'tests/ldap_test_server/test_info.json',
                                                'tests/ldap_test_server/test_schema.json')

    users = {}

    @classmethod
    def construct_dn(cls, username: str, ou: str = None) -> str:
        """
            This function constructs a distinguished name for a username

            :param username: The username of the user
            :type username: str
            :param ou: The optional Organizational Unit to include the user in
            :type ou: str
            :returns: The distinguished name of the user
            :rtype: str
        """

        if ou:
            return f'cn={username},ou={ou},{settings.LDAP_BASE_CONTEXT}'
        else:
            return f'cn={username},{settings.LDAP_BASE_CONTEXT}'

    @classmethod
    def extract_ou(cls, username: str) -> Optional[str]:
        """
            This function gets the organizational unit a test user is in from their username

            :param username: The username to get the ou for
            :type username: str
            :returns: The user's ou (if applicable)
            :rtype: str
        """

        user = cls.users.get(username, {'ou': None})
        return user.get('ou')

    @classmethod
    def create_fake_user(cls, conn: Connection, username: str, password: str, first: str, last: str, ou: str = None):
        """
            This function creates a fake user to use in testing

            :param conn: The (fake) connection to create the user on
            :type conn: Connection
            :param username: The username of the user (domain\\username)
            :type username: str
            :param password: The password of the user
            :type password: str
            :param first: The first name of the user
            :type first: str
            :param last: The last name of the user
            :type last: str
            :param ou: The optional Organizational Unit to include the user in
            :type ou: str
        """

        distinguished_name = cls.construct_dn(username, ou=ou)
        conn.strategy.add_entry(distinguished_name, {
            'objectGUID': str(uuid4()),
            'objectClass': 'user',
            'distinguishedName': distinguished_name,
            'msDs-principalName': f"{settings.LDAP_DOMAIN}\\{username}",
            'userPassword': password,
            'givenName': first,
            'sn': last,
        })

    @classmethod
    def create_fake_users(cls, conn: Connection):
        """
            This function creates a series of fake users from a predefined list

            :param conn: The (fake) connection to create the users on
            :type conn: Connection
        """

        for username in cls.users.keys():
            user = cls.users.get(username)
            cls.create_fake_user(conn, username, user['password'], user['first'], user['last'], user['ou'])

    @classmethod
    def get_connection(cls, username: str, password: str) -> Connection:
        """
            This function overrides the base LDAPAuthentication function to provide a fake connection
            instead of a real one

            :param username: The username to log in with (domain\\user)
            :type username: str
            :param password: The password to log in with
            :type password: str
            :returns: The connection to use
            :rtype: Connection
        """

        cls.setup_server()
        username = username.split('\\')[1]
        conn = Connection(cls.server, cls.construct_dn(username, ou=cls.extract_ou(username)), password,
                          client_strategy=MOCK_SYNC)
        cls.create_fake_users(conn)
        return cls.bind_connection(conn)
