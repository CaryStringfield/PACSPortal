# Django imports
from django.db import models
from django.core.urlresolvers import reverse
import logging
import pytz

# Nucleus imports
from nucleus.auth import UserCredentials

class UserManager(models.Manager):
    def get_queryset(self):
        creds = UserCredentials()
        return super(UserManager, self).get_queryset().filter(created_by = creds.get_OUNetID())

class PACSModel(models.Model):
    """
    Abstract model with fields for the user and timestamp of a row's creation
    and last update.
    .. note:: - 
    """
    creds = UserCredentials()
    
    last_updated_by = models.CharField(max_length=8, default=creds.get_OUNetID(), blank=True, null=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=8, default=creds.get_OUNetID(), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    user_objects = UserManager()
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        creds = UserCredentials()
        self.last_updated_by = creds.get_OUNetID()
        if self.created_by is None:
            self.created_by = creds.get_OUNetID()
        return super(PACSModel,self).save(*args, **kwargs)
        
    @property
    def tz_last_updated_at(self):
        from django.utils.timezone import localtime
        return localtime(self.last_updated_at)
    
    @property
    def tz_created_at(self):
        from django.utils.timezone import localtime
        return localtime(self.created_at)

    def __unicode__(self):
        return u'%s' % self.name

    def is_owner(self, user_obj):
        creds = UserCredentials()
        return self.created_by == creds.get_OUNetID() 

    def can_update(self, user_obj):
        return True

    def can_delete(self, user_obj):
        creds = UserCredentials()
        return self.created_by == creds.get_OUNetID() or creds.is_admin()

    def can_create(self, user_obj):
        return True

    def can_view_list(self, user_obj):
        return True

    def can_view(self, user_obj):
        return True
