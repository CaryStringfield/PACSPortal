from django import forms
from toolkit.forms import CCESimpleSearchForm, CCEModelSearchForm, CCEModelForm
from models import Announcement


class AnnouncementSimpleSearch(CCESimpleSearchForm):
    search_placeholder = 'Search Announcements'
    
    class Meta(CCESimpleSearchForm.Meta):
        model = Announcement
        
        field_lookups = {'search': ('name__icontains',
                                    'body__icontains',
                                    'school__icontains')}


class AnnouncementAdvancedSearchForm(CCEModelSearchForm):
    """Advanced Search Form for Boards"""
    #Body = forms.TextField()

    class Meta:
        model = Announcement
        field_lookups = {
            'name': 'name__icontains',
            'body': 'body__icontains',
        }

        fields = (
            'name',
            'body',
        )

        labels = {
            'name': 'name'
        }


class AnnouncementForm(CCEModelForm):
    class Meta:
        model = Announcement
        fields = ('name',
                  'body',
                  #'author',
                  #'last_updated_by',
                  #'created_by',
                  'school',)
