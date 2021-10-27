# TODO: Error checking and showing it if we can't connect to ActiveDirectory

from ldap3 import Connection, Server, ALL, ObjectDef, Reader, NTLM
from django.conf import settings
from django.auth.backends import BaseBackend

from models import User

class LDAPAuthentication(BaseBackend):
  
  server = Server(settings.LDAP_URL, get_info=ALL)
  
  def create_from_ldap(ldap_user) -> User:
    new_user = User.objects.create_user(id=ldap_user.uid, username=ldap_user.name, first_name=ldap_user.givenName, last_name=ldap_user.sn, email=ldap_user.mail)
    new_user.save()
    return new_user
  
  def get_ldap_user(conn, ldap_id):
    user_obj = ObjectDef('user', conn)
    reader = Reader(conn, user_obj, f'name={ldap_id},{settings.LDAP_BASE_CONTEXT}')
    reader.search()
    if len(reader) == 1:
      return reader[0]
    else:
      return None
  
  def authenticate(self, request, username=None, password=None):
    with Connection(setup_server(), user=f'{settings.LDAP_DOMAIN}\\{username}', password=password, authentication=NTLM) as conn:
      ldap_id = conn.extend.standard.who_am_i()
      ldap_user = self.get_ldap_user(conn, ldap_id)
      if ldap_user is None:
        return None
      else:
        if User.objects.filter(id=ldap_user.uid).exists():
          return User.objects.get(id=ldap_user.uid)
        else:
          return self.create_from_ldap(ldap_user)
    
