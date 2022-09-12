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
    def setup_server(cls) -> None:
        """
            This function constructs a fake server to connect to
        """

        if cls.server is None:
            cls.server = Server.from_definition('fake_server',
                                                'tests/ldap_test_server/test_info.json',
                                                'tests/ldap_test_server/test_schema.json')

    users = {}
    raw_users = {}

    @classmethod
    def construct_dn(cls, username: str) -> str:
        """
            This function constructs a distinguished name for a username

            :param username: The username of the user
            :type username: str
            :returns: The distinguished name of the user
            :rtype: str
        """

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
    def create_user_manual(cls, conn: Connection, dn: str, user: dict) -> None:
        """
            This function creates a user manually without automatic setup of the dn and other values

            :param dn: Distinguished name of the user
            :type dn: str
            :param user: The dictionary to use when creating the user entry
            :type user: dict
        """

        conn.strategy.add_entry(dn, user)

    @classmethod
    def create_fake_user(cls, conn: Connection, username: str, email: str, password: str, first: str, last: str, ou: str = None) -> None:
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

        distinguished_name = cls.construct_dn(username)
        conn.strategy.add_entry(distinguished_name, {
            'objectGUID': str(uuid4()),
            'objectClass': 'user',
            'mail': email,
            'distinguishedName': distinguished_name,
            'msDs-principalName': f"{settings.LDAP_DOMAIN}\\{username}",
            'userPassword': password,
            'givenName': first,
            'sn': last,
        })

    @classmethod
    def create_fake_users(cls, conn: Connection) -> None:
        """
            This function creates a series of fake users from a predefined list

            :param conn: The (fake) connection to create the users on
            :type conn: Connection
        """

        for username in cls.users.keys():
            user = cls.users.get(username)
            cls.create_fake_user(conn, username, f"{username}@example.com", user['password'], user['first'], user['last'], user['ou'])
        for dn in cls.raw_users.keys():
            user = cls.raw_users.get(dn)
            cls.create_user_manual(conn, dn, user)

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
        dn = cls.construct_dn(username) if username not in [k.split(',')[0].split('=')[1] for k in cls.raw_users.keys()] else f"cn={username},ou=EvilPeople,dc=example,dc=com"
        conn = Connection(cls.server, dn, password,
                          client_strategy=MOCK_SYNC)
        cls.create_fake_users(conn)
        return cls.bind_connection(conn)
