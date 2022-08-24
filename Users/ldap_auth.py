"""
    This file is used to provide authentication via LDAP (ActiveDirectory)
"""

from typing import Optional
from uuid import UUID

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from ldap3 import Connection, Server, ALL, ObjectDef, Reader, NTLM, Entry
from ldap3.core.exceptions import LDAPSocketOpenError

from .ldap_errors import LDAPConnectionError, LDAPInvalidCredentials, LDAPAuthException
from .models import User


class LDAPAuthentication(BaseBackend):
    """
        This authentication backend will log in the user to ldap and then create a User in the database
        with the same info.

        :cvar server: The server we're connecting to with LDAP (Must be an ActiveDirectory Server)
    """

    server = None

    @classmethod
    def setup_server(cls) -> None:
        """
            This function gets the server to authenticate with
        """

        if cls.server is None:
            cls.server = Server(settings.LDAP_URL, get_info=ALL)

    @staticmethod
    def bind_connection(conn: Connection) -> Connection:
        """
            This function is used to bind a connection

            :param conn: The Connection to bind
            :type conn: Connection
            :returns: The bound connection
            :rtype: Connection
        """

        try:
            success = conn.bind()
            if success:
                return conn
            else:
                raise LDAPInvalidCredentials()
        except LDAPSocketOpenError:
            raise LDAPConnectionError()

    @classmethod
    def get_connection(cls, username: str, password: str) -> Connection:
        """
            This function is used to get a Connection object to the server with the given credentials

            :param username: The username to log in with (domain\\username)
            :type username: str
            :param password: The password to log in with
            :type username: str
        """

        cls.setup_server()
        conn = Connection(cls.server, user=username, password=password, authentication=NTLM)
        return cls.bind_connection(conn)

    @staticmethod
    def ldap_empty(value) -> str:
        """
            This function will return an empty string if the given Entry's attribute is empty

            :param value: The value to check
            :returns: The attribute as either an empty string or the attribute
            :rtype: str
        """

        return str(value) if str(value) != "[]" else ""

    @staticmethod
    def get_session_from_ldap(ldap_user: Entry) -> str:
        """
            This function takes an LDAP user and gets their session

            :param ldap_user: The user to get the session of
            :type ldap_user: Entry
            :returns: A string ("AM" or "PM") that denotes the user's session
            :rtype: str
        """

        session_raw = str(ldap_user['distinguishedName']).split(',')[1].split('=')[1]
        return session_raw if session_raw == "AM" or session_raw == "PM" else "AM"

    @staticmethod
    def check_user_is_admin(ldap_user: Entry) -> bool:
        """
            This function is used to check if a given ldap user is an administrator

            :param ldap_user: The user to check
            :type ldap_user: Entry
            :returns: A boolean indicating if the user is an administrator
            :rtype: bool
        """

        return ("AM" in str(ldap_user["distinguishedName"]) or "PM" in str(ldap_user["distinguishedName"])) is False

    def update_from_ldap(self, ldap_user: Entry, django_user: User) -> User:
        """
            This function takes an LDAP user and a django user and syncs their data

            :param ldap_user: The ldap user to sync from
            :type ldap_user: Entry
            :param django_user: The django user to sync to
            :type django_user: User
            :returns: The updated django user
            :rtype: User
        """

        django_user.username = ldap_user["msDS-PrincipalName"]
        django_user.first_name = self.ldap_empty(ldap_user.givenName)
        django_user.last_name = self.ldap_empty(ldap_user.sn)
        django_user.session = self.get_session_from_ldap(ldap_user)
        django_user.save()
        return django_user

    def create_from_ldap(self, ldap_user: Entry, guid: str) -> User:
        """
            This function creates a django user from an LDAP user

            :param ldap_user: The user to read from
            :type ldap_user: Entry
            :param guid: The objectGUID of the user
            :type guid: str
            :returns: The new django user
            :rtype: User
        """

        create_method = User.objects.create_superuser if self.check_user_is_admin(
            ldap_user) else User.objects.create_user
        new_user = create_method(id=UUID(guid), username=ldap_user["msDS-PrincipalName"],
                                 first_name=self.ldap_empty(ldap_user.givenName),
                                 last_name=self.ldap_empty(ldap_user.sn),
                                 session=self.get_session_from_ldap(ldap_user),
                                 email=self.ldap_empty(ldap_user.mail))
        new_user.set_unusable_password()
        new_user.save()
        return new_user

    @staticmethod
    def get_all_users(conn: Connection) -> Reader:
        """
            This function is used to get all users in the ActiveDirectory database

            :param conn: The Connection to use for the query
            :type conn: Connection
            :returns: A Reader object that contains all users in the database
            :rtype: Reader
        """

        user_obj = ObjectDef('user', conn)
        reader = Reader(conn, user_obj, settings.LDAP_BASE_CONTEXT)
        reader.search()
        return reader

    def get_ldap_user(self, conn: Connection, username: str) -> Optional[Entry]:
        """
            This function gets an LDAP user from the LDAP server

            :param conn: The connection for the server
            :type conn: Connection
            :param username: The username (MsDs-principalName) to check for
            :type username: str
            :returns: The user that matches the username, if any
            :rtype: User
        """

        reader = self.get_all_users(conn)
        results = reader.match("msDS-PrincipalName", username)
        return results[0]

    def authenticate(self, request, username: str = None, password: str = None) -> Optional[User]:
        """
            This is the function that django uses to authenticate a user

            :param request: The request that we're trying to authenticate
            :param username: The username we're authenticating with
            :param password: The password we're authenticating with
            :returns: the user we wish to authenticate with the request, if any
            :rtype: User
        """

        try:
            conn = self.get_connection(f'{settings.LDAP_DOMAIN}\\{username}', password)
            ldap_user = self.get_ldap_user(conn, f"{settings.LDAP_DOMAIN}\\{username}")
            guid = str(ldap_user["objectGUID"])
            if User.objects.filter(id=UUID(guid)).exists():
                return self.update_from_ldap(ldap_user, User.objects.get(id=UUID(guid)))
            else:
                return self.create_from_ldap(ldap_user, guid)
        except LDAPInvalidCredentials:
            return None
        except LDAPConnectionError:
            if settings.DEBUG is False:
                messages.add_message(request, messages.ERROR,
                                     "There was an error contacting the auth server, please try again later.")
            return None

    def get_user(self, user_id: str) -> Optional[User]:
        """
            This function gets a user given their id

            :param user_id: The id of the user
            :type user_id: str
            :returns: The User that has the id, if any
            :rtype: User
        """

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def delete_old_users(self, username: str, password: str) -> None:
        """
            This function is used to delete any users that are no longer in the ActiveDirectory database.

            :param username: The username to use to log in via LDAP
            :type username: str
            :param password: The password to use to log in via LDAP
            :type password: str
        """

        try:
            conn = self.get_connection(username, password)
            ldap_user = self.get_ldap_user(conn, username)
            if self.check_user_is_admin(ldap_user):
                to_check = User.objects.filter(is_superuser=False).filter(
                    Q(password__startswith='!') | Q(password__isnull=True))
                ldap_users = self.get_all_users(conn)
                for user in to_check:
                    if len(ldap_users.match("msDs-principalName", user.username)) == 0:
                        user.delete()
            else:
                raise LDAPAuthException("You lack permissions to perform this action.")
        except LDAPInvalidCredentials:
            raise LDAPAuthException("The password you provided was incorrect, please check it and try again.")
        except LDAPConnectionError:
            raise LDAPAuthException("Can't connect to ActiveDirectory, please try again later.")
