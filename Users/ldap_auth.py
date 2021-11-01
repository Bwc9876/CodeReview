from typing import Optional
from uuid import UUID

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.backends import BaseBackend
from ldap3 import Connection, Server, ALL, ObjectDef, Reader, NTLM, Entry
from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError

from .models import User


class LDAPAuthentication(BaseBackend):
    server = Server(settings.LDAP_URL, get_info=ALL)

    @staticmethod
    def ldap_empty(value) -> str:
        return value if str(value) != "[]" else ""

    def update_from_ldap(self, ldap_user: Entry, django_user: User) -> User:
        django_user.username = ldap_user["msDS-PrincipalName"]
        django_user.first_name = self.ldap_empty(ldap_user.givenName)
        django_user.last_name = self.ldap_empty(ldap_user.sn)
        django_user.email = self.ldap_empty(ldap_user.mail)
        django_user.save()
        return django_user

    def create_from_ldap(self, ldap_user: Entry, guid: str) -> User:
        new_user = User.objects.create_user(id=UUID(guid), username=ldap_user["msDS-PrincipalName"],
                                            first_name=self.ldap_empty(ldap_user.givenName),
                                            last_name=self.ldap_empty(ldap_user.sn),
                                            email=self.ldap_empty(ldap_user.mail))
        new_user.save()
        return new_user

    def get_ldap_user(self, conn: Connection, username: str) -> Optional[Entry]:
        user_obj = ObjectDef('user', conn)
        reader = Reader(conn, user_obj, settings.LDAP_BASE_CONTEXT)
        reader.search()
        results = reader.match("msDS-PrincipalName", username)
        if len(results) == 1:
            return results[0]
        else:
            return None

    def authenticate(self, request, username: str = None, password: str = None) -> Optional[User]:
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
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
