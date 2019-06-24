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

class CropTool(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['staff_tools', 'crop_tool']
    template_name = 'crop_tool.html'
    page_title = 'Crop Tool'            
        
class ButtonMaker(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['staff_tools', 'button_maker']
    template_name = 'button_maker.html'
    page_title = 'Button Maker'        
    
class BannerMaker(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['staff_tools', 'banner_maker']
    template_name = 'banner_maker.html'
    page_title = 'Banner Maker'            
       
      