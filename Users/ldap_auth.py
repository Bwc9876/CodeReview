from typing import Optional
from uuid import UUID

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import BaseBackend
from ldap3 import Connection, Server, ALL, ObjectDef, Reader, NTLM, Entry
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError

from .models import User


class LDAPAuthentication(BaseBackend):
    """
        This authentication backend will login the user to ldap and then create a User in the database
        with the same info.

        :cvar server: The server we're connecting to with LDAP (Must be an ActiveDirectory Server)
    """

    server = Server(settings.LDAP_URL, get_info=ALL)

    @staticmethod
    def ldap_empty(value) -> str:
        """
            This function will return an empty string if the given Entry's attribute is empty

            :param value: The value to check
            :returns: The attribute as either an empty string or the attribute
            :rtype: str
        """

        return value if str(value) != "[]" else ""

    def update_from_ldap(self, ldap_user: Entry, django_user: User) -> User:
        """
            This function takes an ldap user and a django user and syncs their data

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
        django_user.email = self.ldap_empty(ldap_user.mail)
        django_user.save()
        return django_user

    def create_from_ldap(self, ldap_user: Entry, guid: str) -> User:
        """
            This function creates a django user from an ldap user

            :param ldap_user: The user to read from
            :type ldap_user: Entry
            :param guid: The objectGUID of the user
            :type guid: str
            :returns: The new django user
            :rtype: User
        """

        new_user = User.objects.create_user(id=UUID(guid), username=ldap_user["msDS-PrincipalName"],
                                            first_name=self.ldap_empty(ldap_user.givenName),
                                            last_name=self.ldap_empty(ldap_user.sn),
                                            email=self.ldap_empty(ldap_user.mail))
        new_user.save()
        return new_user

    def get_ldap_user(self, conn: Connection, username: str) -> Optional[Entry]:
        """
            This function gets an ldap user from the ldap server

            :param conn: The connection for the server
            :type conn: Connection
            :param username: The username (MsDs-principalName) to check for
            :type username: str
            :returns: The user that matches the username, if any
            :rtype: User
        """

        user_obj = ObjectDef('user', conn)
        reader = Reader(conn, user_obj, settings.LDAP_BASE_CONTEXT)
        reader.search()
        results = reader.match("msDS-PrincipalName", username)
        if len(results) == 1:
            return results[0]
        else:
            return None

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
            conn = Connection(self.server, user=f'{settings.LDAP_DOMAIN}\\{username}', password=password,
                              authentication=NTLM)
            success = conn.bind()
            if success:
                ldap_id = conn.extend.standard.who_am_i()[2:]
                ldap_user = self.get_ldap_user(conn, ldap_id)
                guid = str(ldap_user["objectGUID"])
                if ldap_user is None:
                    return None
                else:
                    if User.objects.filter(id=UUID(guid)).exists():
                        return self.update_from_ldap(ldap_user, User.objects.get(id=UUID(guid)))
                    else:
                        return self.create_from_ldap(ldap_user, guid)
            else:
                return None
        except LDAPBindError:
            return None
        except LDAPSocketOpenError:
            if not settings.DEBUG:
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
