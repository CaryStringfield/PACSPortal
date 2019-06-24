# Django Imports
from django import forms
from django.forms import BaseFormSet
from django.utils.translation import ugettext as _

from datetime import datetime, timedelta, tzinfo, date, time

# Toolkit base forms
from toolkit.forms import CCESimpleSearchForm, CCEModelSearchForm, CCEModelForm

# Models
from models import Assignment, Student, Submission
from canvas.models import Course as CanvasCourse
import logging


class CourseSimpleSearch(CCESimpleSearchForm):
    search_placeholder = 'Search Courses'

    class Meta(CCESimpleSearchForm.Meta):
        model = CanvasCourse
        field_lookups = {'search': ('id__icontains',
                                    'name__icontains')}
        
class AssignmentSimpleSearch(CCESimpleSearchForm):
    search_placeholder = 'Search Assignments'

    class Meta(CCESimpleSearchForm.Meta):
        model = Assignment
        field_lookups = {'search': ('id__icontains',
                                    'name__icontains')}
        
class StudentSimpleSearch(CCESimpleSearchForm):
    search_placeholder = 'Search Students'

    class Meta(CCESimpleSearchForm.Meta):
        model = Student
        field_lookups = {'search': ('id__icontains',
                                    'name__icontains')}
        
class SubmissionSimpleSearch(CCESimpleSearchForm):
    search_placeholder = 'Search Submissions'

    class Meta(CCESimpleSearchForm.Meta):
        model = Submission
        field_lookups = {'search': ('id__icontains',
                                    'student_id__icontains')}
        
class AssignmentDatesForm(forms.ModelForm): 
    
    class Meta:
        model = Assignment
        fields = [
        'name',
        'start_date',
        'due_date',
        'end_date', 
        'has_override',
        'is_quiz',
        ]

        widgets = { 'name' :forms.TextInput(attrs={'readonly':'readonly', 'class' : 'grey-text', 'size' : '25'}),
                    'start_date' : forms.DateInput(format = '%m/%d/%Y', attrs ={ 'class' : 'datepicker'}),
                    'due_date' : forms.DateInput(format = '%m/%d/%Y', attrs ={ 'class' : 'datepicker' }),
                    'end_date' : forms.DateInput(format = '%m/%d/%Y', attrs ={ 'class' : 'datepicker' }),}
    
    def clean(self):
        cleaned_data = super(AssignmentDatesForm, self).clean()
        start_date = cleaned_data.get("start_date")
        due_date = cleaned_data.get("due_date")
        end_date = cleaned_data.get("end_date")
        errors = []
        date_not_blank = False
        if start_date or due_date or end_date:
            date_not_blank = True  
        
        if date_not_blank and (start_date == None or due_date == None or end_date == None):
            errors += forms.ValidationError( 
                _('All dates must have values or be empty. Cannot change one without others.'),
            )
        else:
            if start_date > due_date:
                #logging.warning("ERROR: start_date > due_date")
                errors += forms.ValidationError( 
                    _('Start Date: %(start_date)s must come before Due Date: %(due_date)s'),
                    params={'start_date': datetime.strftime(start_date, '%m/%d/%Y'),
                            'due_date': datetime.strftime(due_date, '%m/%d/%Y'),},
                    )
            if due_date > end_date:
                #logging.warning("ERROR: due_date > end_date")
                errors += forms.ValidationError(
                    _('Due Date: %(due_date)s must come before End Date: %(end_date)s'),
                    params={'due_date': datetime.strftime(due_date, '%m/%d/%Y'),
                            'end_date': datetime.strftime(end_date, '%m/%d/%Y'),},
                    )
            if start_date > end_date:
                #logging.warning("ERROR: start_date > end_date")
                errors += forms.ValidationError(
                    _('Start Date: %(start_date)s must come before End Date: %(end_date)s'),
                    params={'start_date': datetime.strftime(start_date, '%m/%d/%Y'),
                            'end_date': datetime.strftime(end_date, '%m/%d/%Y'),},
                    )
        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data
    
    def has_changed(self):
        result = False
        
        if 'start_date' in self.changed_data:
            result = True
        if 'due_date' in self.changed_data:
            result = True
        if 'end_date' in self.changed_data:
            result = True
            
        return result
        
        



