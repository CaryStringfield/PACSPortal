import logging
from django.core.exceptions import PermissionDenied
from nucleus.auth import UserCredentials

def is_member(function, groups):
    #self.groups = groups
    def wrap(request, *args, **kwargs):
        creds = UserCredentials()
        if creds.is_member(groups) or creds.is_admin():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def is_admin(function):

    def wrap(request, *args, **kwargs):
        creds = UserCredentials()
        if creds.is_admin():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


