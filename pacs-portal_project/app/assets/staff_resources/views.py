from django.shortcuts import render
# Create your views here.
from django.contrib import messages
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.conf import settings

from canvasapi import Canvas
from django.views.generic import TemplateView
import requests, os, logging

# Toolkit imports
from toolkit.views import  CCETemplateView, CCECreateView, CCECreateWithInlinesView, CCEDeleteView, CCEDetailView, \
    CCEFormView, CCEListView, CCEModelFormSetView, CCEObjectRedirectView, CCERedirectView, \
    CCESearchView, CCETemplateView, CCEUpdateView,  CCEUpdateWithInlinesView, \
    ReportDownloadDetailView, ReportDownloadSearchView

# User Credentials retrieval/mixins
from nucleus.auth import UserCredentials
from nucleus.mixins import CurrentUserMixin
from forms import AnnouncementSimpleSearch, AnnouncementForm
from models import Announcement


class DashboardView(CurrentUserMixin, CCESearchView):
    sidebar_group = ['dashboard', ]
    template_name = 'dashboard.html'
    page_title = "Announcements"
    search_form_class = AnnouncementSimpleSearch
   
    success_message = "success"
    model = Announcement
    show_context_menu = True
    paginate_by = 14
    
    columns = [
        ('Title', 'name'),
        ('Body', 'body'),
        ('Author', 'author'),
        ('Date', 'last_updated_at'),
        ('School', 'school'), 
        ('Actions', 'short_school') ,       
    ]
    
    def get_queryset(self):
        return super(DashboardView, self).get_queryset()\
            .all().order_by('-last_updated_at' , 'name')
            
class AnnouncementCreateView(CurrentUserMixin, CCECreateView):
    model = Announcement
    form_class = AnnouncementForm
    page_title = "Add Announcement!"
    sidebar_group = ['dashboard', ]
    success_message = "Announcement Created Successfully"
    creds = UserCredentials()
    
    def get_success_url(self):
        return reverse('dashboard')
    
class AnnouncementUpdateView(CurrentUserMixin, CCEUpdateView):
    model = Announcement
    form_class = AnnouncementForm
    page_title = 'Edit Announcement'
    sidebar_group = ['dashboard', ]    
    success_message = "Announcement Edited Successfully"
    
    def get_success_url(self):
        return reverse('dashboard')

class AnnouncementDeleteView(CurrentUserMixin, CCEDeleteView):
    model = Announcement    
    page_title = 'Delete Announcement'    
    sidebar_group = ['dashboard', ]
    success_message = "Announcement Deleted Successfully"

    def get_success_url(self):
        return reverse('dashboard')

class AnnouncementDetailView(CurrentUserMixin, CCEDetailView):
    model = Announcement
    form_class = AnnouncementForm
    page_title = 'Announcement Details'
    sidebar_group = ['dashboard', ]    
    detail_fields = [
        ('Title', 'name'),
        ('Body', 'body'),
        ('Author', 'author'),
        ('School', 'school'),
        ('Created At', 'created_at'),
        ('Created By', 'created_by'),
        ('Last Updated At', 'last_updated_at'),
        ('Last Updated By', 'last_updated_by'),
    ]
    show_context_menu = True
    

    
class CourseWorkloadEstimator(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['staff_resources', 'workload-estimator']
    template_name = 'workload-estimator.html'
    page_title = 'Course Workload Estimator'     
    
class LearningOutcomeGenerator(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['staff_resources', 'outcome-generator']
    template_name = 'outcome-generator.html'
    page_title = 'Learning Outcome Generator'     
    
class ObjectiveBuilder(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['staff_resources', 'objective_builder']
    template_name = 'objective_builder.html'
    page_title = 'Objective Builder'        
       
       