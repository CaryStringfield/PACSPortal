from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from pickle import FALSE
from datetime import datetime, timedelta, tzinfo, date, time
from nucleus.models import PACSModel
import pytz

# Nucleus imports
from nucleus.auth import UserCredentials


class Announcement(PACSModel):
    name = models.CharField(max_length=50)
    body = models.TextField()
    author = models.CharField(max_length=50)    
    #School = models.ForeignKey('Schools', on_delete=models.CASCADE,)
    General = 'General'
    #Academic_Curriculum_and_Policies_Council = 'Academic Curriculum and Policies Council'
    Aviation_Studies = 'Aviation Studies'
    Leadership_Studies = 'Leadership Studies'
    Criminal_Justice_Studies = 'Criminal Justice Studies'
    Human_and_Health_Services_Studies = 'Human and Health Services Studies'
    Integrative_and_Cultural_Studies = 'Integrative and Cultural Studies'
    Campus_Affiliated_Programs = 'Campus Affiliated Programs'
    English_Language_Learner_Programs = 'English Language Learner Programs'
    Lifelong_Learning_Programs = 'Lifelong Learning Programs'
    
    School_Choices = (
        
        (General , 'General'),
        #(Academic_Curriculum_and_Policies_Council, 'Academic Curriculum and Policies Council'),
        (Aviation_Studies , 'Aviation Studies'),
        (Leadership_Studies , 'Leadership Studies'),
        (Criminal_Justice_Studies , 'Criminal Justice Studies'),
        (Human_and_Health_Services_Studies , 'Human and Health Services Studies'),
        (Integrative_and_Cultural_Studies , 'Integrative and Cultural Studies'),
        (Campus_Affiliated_Programs , 'Campus Affiliated Programs'),
        (English_Language_Learner_Programs , 'English Language Learner Programs'),
        (Lifelong_Learning_Programs , 'Lifelong Learning Programs'),

        )
    
    school = models.CharField(max_length=50, choices = School_Choices, default = General,)
    short_school = models.CharField(max_length=15, null = True, editable=False,)
    
    def fillshort(self):
        short = ''        
        if self.school == 'General':
             short = 'general' 
        #if self.school == 'Academic Curriculum and Policies Council':
        #     short = 'curriculum' 
        if self.school == 'Aviation Studies':
             short = 'aviation' 
        if self.school == 'Leadership Studies':
             short = 'leadership'
        if self.school == 'Criminal Justice Studies':
             short = 'criminal' 
        if self.school == 'Human and Health Services Studies':
             short = 'human' 
        if self.school == 'Integrative and Cultural Studies':
             short = 'integrative' 
        if self.school == 'Campus Affiliated Programs':
             short = 'affiliated' 
        if self.school == 'English Language Learner Programs':
             short = 'english' 
        if self.school == 'Lifelong Learning Programs':
             short = 'lifelong' 
        return short
    
    def get_short_school(self):
        return self.short_school
        
    def save(self,*args,**kwargs):
        creds = UserCredentials()
        self.author = creds.get_FirstName() + " " + creds.get_LastName()
        self.short_school = self.fillshort()
        return super(Announcement, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('view_announcement', kwargs={'pk': self.pk})

    