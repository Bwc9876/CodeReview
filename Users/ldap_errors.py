"""
    This file lists errors related to LDAP Authentication
"""


class LDAPAuthException(Exception):
    """
        This exception is used to represent an error with authenticating through LDAP
    """

    pass


class LDAPInvalidCredentials(LDAPAuthException):
    """
        This exception is used when the credentials provided are invalid
    """

    pass


class LDAPConnectionError(LDAPAuthException):
    """
        This exception is used when we can't contact ActiveDirectory
    """
