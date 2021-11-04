from ldap3 import Server, Connection, ALL, MOCK_SYNC, ObjectDef, AttrDef
from django.test import TestCase, Client

class TestLdap(TestCase):

    def setUp(self) -> None:
        #Add Setup Code
        pass

    def test_create_user(self) -> None:
        # Test creating users on login
        pass

    def test_update_user(self) -> None:
        # Test updating a user's info when they login
        pass

    def test_sync(self) -> None:
        # Test syncing users from ActiveDirectory to Django
        pass
