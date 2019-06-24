from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

# Nucleus imports 
from nucleus.mixins import CurrentUserMixin
from nucleus.auth import UserCredentials
from nucleus.api import CanvasAPI

# Library imports
from datetime import datetime, timedelta, tzinfo, date, time
import logging
import requests

# Toolkit views
from toolkit.views import CCECreateView, CCECreateWithInlinesView, CCEDeleteView, CCEDetailView, \
    CCEFormView, CCEListView, CCEModelFormSetView, CCEObjectRedirectView, CCERedirectView, \
    CCESearchView, CCETemplateView, CCEUpdateView,  CCEUpdateWithInlinesView, \
    ReportDownloadDetailView, ReportDownloadSearchView

# Form imports
from forms import CourseSimpleSearchForm, CourseAdvancedSearchForm, StudentSimpleSearchForm, TermSimpleSearchForm, SubaccountSimpleSearchForm
from forms import AssignmentSimpleSearchForm, AssignmentAdvancedSearchForm, StudentCourseSimpleSearchForm, StudentCourseAdvancedSearchForm
from models import Course, Student, Term, Subaccount
from faculty_tools.models import Assignment, StudentCourse


class CourseListView(CurrentUserMixin, CCESearchView):
    model = Course
    page_title = 'Course List'
    search_form_class = CourseSimpleSearchForm
    advanced_search_form_class = CourseAdvancedSearchForm
    sidebar_group = ['faculty_tools', 'canvas_course_list']
    columns = [
        ('Course ID', 'course_id'),
        ('Name', 'name'),
        ('Course Code', 'course_code'),
        ('Subaccount', 'subaccount'),
        ('Term', 'term')
    ]
    paginate_by = 50
    
    def render_buttons(self, user, obj, *args, **kwargs):
        buttons = super(CourseListView, self).render_buttons(user, obj,
                                                            *args, **kwargs)
        
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='View Submissions',
                               icon_classes='glyphicon glyphicon-paste',
                               url= "/ft/canvas_course_list/" + str(obj.course_id) + "/submissions/",
                               label="View Submissions",
                               condensed=False,)
        )
        
        return buttons
    
class AdminCourseListView(CurrentUserMixin, CCESearchView):
    model = Course
    page_title = 'Admin Course List'
    search_form_class = CourseSimpleSearchForm
    advanced_search_form_class = CourseAdvancedSearchForm
    sidebar_group = ['canvas', 'canvas_admincourse_list']
    columns = [
        ('Course ID', 'course_id'),
        ('Name', 'name'),
        ('Course Code', 'course_code'),
        ('Subaccount', 'subaccount'),
        ('Term', 'term')
    ]
    paginate_by = 50
    
    def render_buttons(self, user, obj, *args, **kwargs):
        buttons = super(AdminCourseListView, self).render_buttons(user, obj,
                                                            *args, **kwargs)
        
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='View Students',
                               icon_classes='fas fa-user-graduate',
                               url= "/c/studentcourse/" + str(obj.course_id) + "/",
                               label="View Students",
                               condensed=False,)
        )
        
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='View Assignments',
                               icon_classes='fas fa-book-open',
                               url= "/c/assignment/" + str(obj.course_id) + "/",
                               label="View Assignments",
                               condensed=False,)
        )
        
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='View Submissions',
                               icon_classes='glyphicon glyphicon-paste',
                               url= "/ft/canvas_course_list/" + str(obj.course_id) + "/submissions/",
                               label="View Submissions",
                               condensed=False,)
        )
        
        return buttons
    
class StudentListView(CurrentUserMixin, CCESearchView):
    model = Student
    page_title = 'Student List'
    search_form_class = StudentSimpleSearchForm
    sidebar_group = ['canvas', 'canvas_student_list']
    columns = [
        ('Name', 'sortable_name'),
        ('Login ID', 'login_id'),        
        ('Canvas ID', 'canvas_id'),
        ('SIS ID', 'sis_user_id'),
    ]
    paginate_by = 50
    
class TermListView(CurrentUserMixin, CCESearchView):
    model = Term
    page_title = 'Term List'
    search_form_class = TermSimpleSearchForm
    sidebar_group = ['canvas', 'canvas_term_list']
    columns = [
        ('Term ID', 'term_id'),    
        ('Name', 'name'),
    ]
    paginate_by = 50
    
    def get_queryset(self, *args, **kwargs):
        return super(TermListView,self).get_queryset().order_by('term_id','name')
    
class SubaccountListView(CurrentUserMixin, CCESearchView):
    model = Subaccount
    page_title = 'Subaccount List'
    search_form_class = SubaccountSimpleSearchForm
    sidebar_group = ['canvas', 'canvas_subaccount_list']
    columns = [
        ('Name', 'name'),
        ('Subaccount ID', 'subaccount_id'),        
    ]
    paginate_by = 50
    
    def get_queryset(self, *args, **kwargs):
        return super(SubaccountListView,self).get_queryset().order_by('subaccount_id','name')
    
class AssignmentListView(CurrentUserMixin, CCESearchView):
    model = Assignment
    page_title = 'Assignment List'
    search_form_class = AssignmentSimpleSearchForm
    advanced_search_form_class = AssignmentAdvancedSearchForm
    template_name = 'reloadable_list.html'
    sidebar_group = ['canvas', 'canvas_assignment_list']
    columns = [
        ('Course', 'course'),
        ('Name', 'name'),
        ('Assignment ID', 'assignment_id'),        
        ('Start Date', 'start_date'),
        ('Due Date', 'due_date'),
        ('End Date', 'end_date'),
        ('Has Override?', 'has_override'),
        ('Quiz?', 'is_quiz'),
    ]
    paginate_by = 50
    
    def get(self, request, *args, **kwargs):
        course_id = None
        if 'course_id' in self.kwargs:
            course_id = int(self.kwargs['course_id'])
        reload = request.GET.get('reload', False) == "True"
            
        if course_id is not None:
            existing_records = self.model.objects.filter(course__course_id = course_id).first()
            
            if existing_records is None or reload:
                api = CanvasAPI()
    
                course = Course.objects.filter(course_id = course_id).first()
                self.model.objects.filter(course = course).all().delete()
                json_data = api.get_assignments(course_id)
                json_list = list(json_data) #the data from canvas
                
                for assignment in json_list:   #get the stuff i need from the canvas data
                    assignment_id = assignment['id']
                    assignment_name = assignment['name']             
                    has_override = assignment['has_overrides']
                    is_quiz = assignment['is_quiz_assignment'] 
                    logging.warning("ASSIGNMENT")
                    logging.warning(str(assignment))
                    td = timedelta (hours = 6)#adjust to local time      
                    if assignment['unlock_at'] is not None:
                        unlockCanvas = datetime.strptime(assignment['unlock_at'], '%Y-%m-%dT%H:%M:%SZ')#save in datetime object
                        unlockCanvas = unlockCanvas - td#adjust time.  else it goes past midnight altering the date
                        start_date = datetime.strftime(unlockCanvas, '%Y-%m-%d')#remove time and save just the date as a string
                    else: 
                        start_date = None
                    if assignment['due_at'] is not None:
                        dueCanvas = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
                        dueCanvas = dueCanvas - td
                        due_date = datetime.strftime(dueCanvas, '%Y-%m-%d')#saving date as string and in m/d/y for use with datepicker
                    else:
                        due_date = None
                    if assignment['lock_at'] is not None:
                        lockCanvas = datetime.strptime(assignment['lock_at'], '%Y-%m-%dT%H:%M:%SZ')                
                        lockCanvas = lockCanvas - td 
                        end_date = datetime.strftime(lockCanvas, '%Y-%m-%d')
                    else:
                        end_date = None
                      
                    self.model.user_objects.create(assignment_id = assignment_id, name = assignment_name, start_date = start_date, due_date = due_date, end_date = end_date, has_override = has_override, is_quiz = is_quiz, course = course)
        
        return super(AssignmentListView, self).get(request, *args, **kwargs)
        
    
    def get_queryset(self, *args, **kwargs):
        queryset = super(AssignmentListView,self).get_queryset()
        
        course_id = None
        if 'course_id' in self.kwargs:
            course_id = self.kwargs['course_id']
        
        if course_id is not None:
            queryset = queryset.filter(course__course_id = int(course_id)).all().order_by('name')
        else:
            queryset = queryset.order_by('course__name', 'name')
        return queryset
    
    def get_context_data(self, *args, **kwargs):
        context = super(AssignmentListView, self).get_context_data(*args, **kwargs) 
        course_id = None
        if 'course_id' in self.kwargs:
            course_id = int(self.kwargs['course_id'])
        
        if course_id is not None:
            context['course_id'] = course_id
            load_date = self.model.objects.filter(course__course_id = course_id).order_by('created_at').first()
            
            if load_date is not None:
                context['load_date'] = load_date.created_at
        
        return context
    
class StudentCourseListView(CurrentUserMixin, CCESearchView):
    model = StudentCourse
    page_title = 'Student Course List'
    search_form_class = StudentCourseSimpleSearchForm
    advanced_search_form_class = StudentCourseAdvancedSearchForm
    template_name = 'reloadable_list.html'
    sidebar_group = ['canvas', 'canvas_studentcourse_list']
    columns = [
        ('Student', 'student'),        
        ('Course', 'course'),
    ]
    paginate_by = 50
    
    def get(self, request, *args, **kwargs):
        course_id = None
        if 'course_id' in self.kwargs:
            course_id = int(self.kwargs['course_id'])
        reload = request.GET.get('reload', False) == "True"
            
        if course_id is not None:
            existing_records = self.model.objects.filter(course__course_id = course_id).first()
            
            if existing_records is None or reload:
                api = CanvasAPI()
                course = Course.objects.filter(course_id = course_id).first()
                self.model.objects.filter(course = course).all().delete()
                
                student_list = api.get_students(course_id)
                for student in student_list:
                    localstudent = Student.objects.filter(canvas_id = int(student['id'])).first()
                    if localstudent is not None:
                        self.model.user_objects.create(student = localstudent, course = course)
        
        return super(StudentCourseListView, self).get(request, *args, **kwargs)
    
    def get_queryset(self, *args, **kwargs):
        queryset = super(StudentCourseListView,self).get_queryset()
        
        course_id = None
        if 'course_id' in self.kwargs:
            course_id = self.kwargs['course_id']
        
        if course_id is not None:
            queryset = queryset.filter(course__course_id = int(course_id)).all().order_by('student__sortable_name')
            
        return queryset
    
    def get_context_data(self, *args, **kwargs):
        context = super(StudentCourseListView, self).get_context_data(*args, **kwargs) 
        course_id = None
        if 'course_id' in self.kwargs:
            course_id = int(self.kwargs['course_id'])
        
        if course_id is not None:
            context['course_id'] = course_id
            load_date = self.model.objects.filter(course__course_id = course_id).order_by('created_at').first()
            
            if load_date is not None:
                context['load_date'] = load_date.created_at
        
        return context
    