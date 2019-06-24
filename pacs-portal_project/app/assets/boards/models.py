from django.core.urlresolvers import reverse
from django.db import models
from toolkit.models import CCEAuditModel


class Board(CCEAuditModel):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return u'/b/%s' % self.name

    def get_absolute_url(self):
        return reverse('browse_tasks') + '?boards=%s' % self.pk

    def can_update(self, user_obj):
        return True
        #return True

    def can_delete(self, user_obj):
        return True

    def can_create(self, user_obj):
        return True

    def can_view_list(self, user_obj):
        return True

    def can_view(self, user_obj):
        return True
