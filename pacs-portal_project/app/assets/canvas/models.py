from __future__ import unicode_literals
from django.db import models

# Nucleus imports
from nucleus.models import PACSModel

class Term(PACSModel):
    term_id = models.IntegerField(unique=True)
    name = models.CharField(max_length = 100)

    class Meta:
        ordering = ('term_id',)
        
    def _str_(self):
        return self.term_id, self.name 
    
    def __unicode__(self):
        return u'{0}'.format(self.name)

    def get(self):
        return self.name

class Subaccount(PACSModel):
    parent = models.ForeignKey('self', null=True, related_name='subaccount', on_delete=models.CASCADE,)
    subaccount_id = models.IntegerField(unique = True)
    name = models.CharField(max_length = 100)

    class Meta:
        verbose_name_plural = "Subaccounts"
        ordering = ('name',)

    def _str_(self):
        return self.subaccount_id, self.parent, self.name 
    
    def __unicode__(self):
        return u'{0}'.format(self.name)

    def get(self):
        return self.name

class Course(PACSModel):
    course_id = models.IntegerField(null = True, unique=True)
    name = models.CharField(max_length = 100)
    course_code = models.CharField(max_length = 100)
    term = models.ForeignKey(Term, null=True, on_delete=models.CASCADE,)
    subaccount = models.ForeignKey(Subaccount, null = True, on_delete=models.CASCADE,)
    
    class Meta:
        ordering = ('course_code','name',)
    
    def _str_(self):
        return self.course_id, self.name, self.course_code, self.subaccount_id

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def get(self):
        return self.name
    
class Student(PACSModel):
    canvas_id = models.IntegerField(unique = True)
    name = models.CharField(max_length = 100, null = True)
    sortable_name = models.CharField(max_length = 100, null = True)
    short_name = models.CharField(max_length = 100, null = True)
    sis_user_id = models.CharField(max_length = 100, null = True)
    login_id = models.CharField(max_length = 100)

    class Meta:
        ordering = ('sortable_name','login_id')

    def _str_(self):
        return self.login_id, self.name, self.canvas_id, self.sis_user_id  
    
    def __unicode__(self):
        return u'{0}'.format(self.sortable_name)

    def get(self):
        return self.login_id

