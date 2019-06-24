from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

# Nucleus imports 
from nucleus.mixins import CurrentUserMixin
from nucleus.auth import UserCredentials
from nucleus.api import CanvasAPI
from nucleus import settings

# Toolkit views
from toolkit.views import CCECreateView, CCECreateWithInlinesView, CCEDeleteView, CCEDetailView, \
    CCEFormView, CCEListView, CCEModelFormSetView, CCEObjectRedirectView, CCERedirectView, \
    CCESearchView, CCETemplateView, CCEUpdateView,  CCEUpdateWithInlinesView, \
    ReportDownloadDetailView, ReportDownloadSearchView

# Library imports
from datetime import datetime, timedelta, tzinfo, date, time
import logging
import requests

# Form imports
from faculty_tools.forms import CourseSimpleSearch, AssignmentDatesForm, AssignmentSimpleSearch, StudentSimpleSearch, SubmissionSimpleSearch
from faculty_tools.models import Assignment, Submission, StudentCourse
from canvas.models import Course as CanvasCourse, Student, Subaccount, Term

class CourseListView(CurrentUserMixin, CCESearchView):
    model = CanvasCourse
    page_title = 'Course List'
    search_form_class = CourseSimpleSearch
    success_message = "success"
    sidebar_group = ['faculty_tools', 'course_list']
    columns = [
        ('Course ID', 'course_id'),
        ('Name', 'name'),
    ]
    paginate_by = 20
    show_context_menu = False

    def get(self, request, *args, **kwargs):
        creds = UserCredentials()
        api = CanvasAPI()
        
        canvasID = api.get_canvasID(creds.get_OUNetID())
        api_response = api.get_class_by_teacher(canvasID)
        api_list = list(api_response)
        
        for course in api_list:
            course_id = int(course['id'])
            course_found = self.model.objects.filter(course_id = course_id).first() 

            if course_found is None:
                term_id = settings.CURRENT_TERM
                term = Term.objects.filter(term_id = term_id).first() 
                subaccount = Subaccount.objects.filter(subaccount_id = course['account_id']).first()
                course_create = self.model.objects.create(course_id = course_id, name = course['name'], course_code = course['course_code'], term = term, subaccount = subaccount)
                course_create.save()

        return super(CourseListView, self).get(request, *args, **kwargs)
    
    def get_queryset(self):
        creds = UserCredentials()
        api = CanvasAPI()

        canvasID = api.get_canvasID(creds.get_OUNetID())
        api_response = api.get_class_by_teacher(canvasID)
        api_list = list(api_response)
        
        course_ids = []
        for course in api_list:
            course_ids.append(int(course['id']))

        return self.model.objects.filter(course_id__in =course_ids)
    
    def render_buttons(self, user, obj, *args, **kwargs):
        buttons = super(CourseListView, self).render_buttons(user, obj,
                                                            *args, **kwargs)
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='Edit Assignment Dates',
                               icon_classes='glyphicon glyphicon-edit',
                               url= str(obj.course_id) + "/edit/",
                               label="Edit Assignment Dates",
                               condensed=False,),
        )
        
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='Extend Due Dates',
                               icon_classes='glyphicon glyphicon-paste',
                               url= str(obj.course_id) + "/extend/",
                               label="Extend Due Dates",
                               condensed=False,)
        )
        
        buttons.append(
            self.render_button(btn_class='btn-warning btn-inline',
                               button_text='View Submissions',
                               icon_classes='glyphicon glyphicon-paste',
                               url= str(obj.course_id) + "/submissions/",
                               label="View Submissions",
                               condensed=False,)
        )
        
        return buttons


class EditDueDates(CurrentUserMixin, CCEModelFormSetView):
    model = Assignment
    page_title = 'Edit Due Dates'
    success_message = "Dates updated successfully!"
    add_button_title = "Add Button"
    template_name = "edit_due_dates.html"
    sidebar_group = ['faculty_tools', 'course_list']

    form_class = AssignmentDatesForm
    submit_text = "Save Dates"
    quit_text = "Quit"
    # **Note: Kwargs for formset_factory different than documentation
    #    Set them directly like below:
    extra = 0
    #max_num = None
    #can_order = False
    #can_delete = False
    
    columns = [
        ('Assignment Name', 'name'),
        ('Start Date', 'start_date'),
        ('Due Date', 'due_date'),
        ('End Date', 'end_date'),
        ]

    show_context_menu = False

    def get(self, request, *args, **kwargs):
        creds = UserCredentials()
        api = CanvasAPI()

        course_id = int(self.kwargs['course_id'])
        course = CanvasCourse.objects.filter(course_id = course_id).first()

        api.is_teacher_of_course(course_id, creds.get_OUNetID())
        if not api.is_teacher_of_course(course_id, creds.get_OUNetID()):
            raise PermissionDenied

        if ('assignment_id' in self.kwargs and 'student_id' in self.kwargs):
            self.assignment_id = self.kwargs['assignment_id']
            self.student_id = self.kwargs['student_id']
            self.page_title = "Extend Due Dates"
            
            json_data = api.get_assignment(course_id, self.assignment_id)
            
            override = api.get_assignment_override(course_id, self.assignment_id, self.student_id) 
            if override:
                if 'due_at' in override:
                    json_data['due_at'] = override['due_at']
                else:
                    json_data['due_at'] = None
                if 'unlock_at' in override:
                    json_data['unlock_at'] = override['unlock_at']
                else:
                    json_data['unlock_at'] = None
                if 'lock_at' in override:
                    json_data['lock_at'] = override['lock_at']
                else:
                    json_data['lock_at'] = None
                json_data['has_overrides'] = True
            else:
                json_data['has_overrides'] = False
                
            json_list = [json_data] #the data from canvas

        else:
            json_data = api.get_assignments(course_id)
            json_list = list(json_data) #the data from canvas

        
        for assignment in json_list:   #get the stuff i need from the canvas data
            assignment_id = assignment['id']
            assignment_name = assignment['name']    
            is_quiz = assignment['is_quiz_assignment']
            has_override = assignment['has_overrides']
                        
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
            
            assignment_record = self.model.objects.filter(assignment_id = assignment_id)
            if assignment_record is None:
                self.model.objects.create(assignment_id = assignment_id, name = assignment_name, start_date = start_date, due_date = due_date, end_date = end_date, has_override = has_override, is_quiz = is_quiz, course = course)
            else:
                assignment_record.update(assignment_id = assignment_id, name = assignment_name, start_date = start_date, due_date = due_date, end_date = end_date, has_override = has_override, is_quiz = is_quiz, course = course)
            
        return super(EditDueDates, self).get(request, *args, **kwargs)
        
    def get_queryset(self, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        return self.model.objects.filter(course__course_id = course_id).all()
        
    def get_context_data(self, *args, **kwargs): 
        course_id = int(self.kwargs['course_id'])
        if ('assignment_id' in self.kwargs and 'student_id' in self.kwargs):
            self.assignment_id = self.kwargs['assignment_id']
            self.student_id = self.kwargs['student_id']
        
        data = super(EditDueDates,self).get_context_data(**kwargs)
        api = CanvasAPI()
        creds = UserCredentials()
        if  (hasattr(self,'assignment_id') and hasattr(self,'student_id')):
            data['assignment_id'] = self.assignment_id
            data['assignment_name'] = Assignment.objects.filter(assignment_id = self.assignment_id).first()
            if not data['assignment_name']:
                data['assignment_name'] = api.get_assignment(course_id, self.assignment_id)['name']
            data['student_id'] = self.student_id
            data['student_name'] = Student.objects.filter(canvas_id = self.student_id).first()
            if not data['student_name']:
                data['student_name'] = api.get_user(self.student_id)['name']
            data['is_override_create'] = True
        data['course_id'] = course_id
        data['course_name'] = CanvasCourse.objects.filter(course_id = course_id).first()
        if not data['course_name']:
            data['course_name'] = api.get_courses(course_id)['name']
            
        has_override_dict = {}
        is_quiz_dict = {}
        has_override = False
        
        for object in data['object_list']:
            if object.is_quiz:
                is_quiz_dict[object.id] = True
            else:
                is_quiz_dict[object.id] = True
        for object in data['object_list']:
            if object.has_override:
                has_override_dict[object.id] = True
                has_override = True
            else:
                has_override_dict[object.id] = True
                
        data['has_override_dict'] = has_override_dict
        data['is_quiz_dict'] = is_quiz_dict
        data['has_override'] = has_override

        return data

    def formset_valid(self, formset):
        course_id = self.kwargs['course_id']

        cleaned_data = formset.clean()
        capi = CanvasAPI() 
        creds = UserCredentials()
        
        for form in formset:
            if form.has_changed():
                form.save()

                assignment_id = form.cleaned_data['id'].assignment_id
                has_override = form.cleaned_data['id'].has_override
                
                # Fixed time to add to dates
                starttime = time(0,0,0)
                endtime = time(23,59,00)                
                
                # Get dates from DB
                start_date = form.cleaned_data['start_date']
                due_date = form.cleaned_data['due_date']
                end_date = form.cleaned_data['end_date']
        
                # Combine date with fixed time and convert to isoformat
                start_date_time = datetime.combine(start_date,starttime).isoformat()
                due_date_time = datetime.combine(due_date,endtime).isoformat()
                end_date_time = datetime.combine(end_date,endtime).isoformat()
                
                if ('assignment_id' in self.kwargs and 'student_id' in self.kwargs):
                    self.assignment_id = self.kwargs['assignment_id']
                    self.student_id = self.kwargs['student_id']
                    
                    if has_override:
                        capi.update_assignment_override(course_id, self.assignment_id, self.student_id, due_date_time, start_date_time, end_date_time)
                        self.success_message = "Assignment override updated!"
                    else:
                        capi.create_assignment_override(course_id, self.assignment_id, self.student_id, due_date_time, start_date_time, end_date_time)
                        self.success_message = "Assignment override created!"

                else:
                    if has_override:
                        capi.delete_assignment_overrides(course_id, assignment_id)
                        
                    capi.update_assignment_dates(course_id, assignment_id, due_date_time, start_date_time, end_date_time)    
                
        return super(EditDueDates, self).formset_valid(formset)
    
    def formset_invalid(self, formset):
        for error in formset.errors:
            logging.warning(error)
        return super(EditDueDates, self).formset_invalid(formset)
    
    
class AssignmentListView(CurrentUserMixin, CCESearchView):
    model = Assignment
    page_title = 'Assignment List'
    search_form_class = AssignmentSimpleSearch
    success_message = "success"
    sidebar_group = ['faculty_tools', 'course_list']
    columns = [
        ('Assignment ID', 'assignment_id'),
        ('Assignment Name', 'name'),
    ]
    paginate_by = 20
    show_context_menu = False

    def get(self, request, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        self.model.objects.filter(course__course_id = course_id).delete()
        course = CanvasCourse.objects.filter(course_id = course_id).first()
        api = CanvasAPI()

        json_data = api.get_assignments(course_id)
        json_list = list(json_data) #the data from canvas
        
        for assignment in json_list:   #get the stuff i need from the canvas data
            assignment_id = assignment['id']
            assignment_name = assignment['name']             
            has_override = assignment['has_overrides']
            is_quiz = assignment['is_quiz_assignment']   
            
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
            
            Assignment.user_objects.create(assignment_id = assignment_id, name = assignment_name, start_date = start_date, due_date = due_date, end_date = end_date, has_override = has_override, is_quiz = is_quiz, course = course)
        
        return super(AssignmentListView, self).get(request, *args, **kwargs)
 
    def get_queryset(self, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        return self.model.objects.filter(course__course_id = course_id, is_quiz = False).all()

    def render_buttons(self, user, obj, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        buttons = super(AssignmentListView, self).render_buttons(user, obj,
                                                            *args, **kwargs)
        buttons.append(

            self.render_button(btn_class='btn-warning',
                               button_text='Choose Assignment',
                               icon_classes='glyphicon glyphicon-edit',
                               url=reverse('course_list') + str(course_id) + "/" + str(obj.assignment_id) + '/extend/',
                               label="Choose Assignment",
                               condensed=False,),

        )
        return buttons
    
    
class StudentListView(CurrentUserMixin, CCESearchView):
    model = Student
    page_title = 'Student List'
    search_form_class = StudentSimpleSearch
    success_message = "success"
    sidebar_group = ['faculty_tools', 'course_list']
    columns = [
        ('Student ID', 'canvas_id'),
        ('Student Name', 'name'),
    ]
    paginate_by = 20
    show_context_menu = False

    def get(self, request, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        StudentCourse.objects.filter(course__course_id = course_id).delete()
        course = CanvasCourse.objects.filter(course_id = course_id).first()
        api = CanvasAPI()
        assignment_id = self.kwargs['assignment_id']
        
        json_data = api.get_students(course_id)
        json_list = list(json_data) #the data from canvas

        for student_record in json_list:   #get the stuff i need from the canvas data
            student_id = student_record['id']
            student = Student.objects.filter(canvas_id = int(student_id)).first()
            if student is not None:
                StudentCourse.user_objects.create(student = student, course = course)
        
        return super(StudentListView, self).get(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        results = self.model.objects.filter(studentcourse__course__course_id = course_id).all()
        return results

    def render_buttons(self, user, obj, *args, **kwargs):
        buttons = super(StudentListView, self).render_buttons(user, obj,
                                                            *args, **kwargs)
        
        course_id = int(self.kwargs['course_id'])
        assignment_id = int(self.kwargs['assignment_id'])
        
        buttons.append(

            self.render_button(btn_class='btn-warning',
                               button_text='Choose Student',
                               icon_classes='glyphicon glyphicon-edit',
                               url=reverse('course_list') + str(course_id) + "/" + str(assignment_id) + '/' + str(obj.canvas_id) + '/extend/',
                               label="Choose Student",
                               condensed=False,),

        )
        return buttons
    
class SubmissionListView(CurrentUserMixin, CCESearchView):
    model = Submission
    page_title = 'Submissions List'
    search_form_class = StudentSimpleSearch
    success_message = "success"
    template_name = 'submissions_template.html'
    sidebar_group = ['faculty_tools', 'canvas_course_list']
    columns = [
        ('Student', 'student'),
        ('Assignment', 'assignment'),
        ('Submitted', 'submitted'),
        ('Late', 'late'),
    ]
    show_context_menu = False
    
    def get(self, request, *args, **kwargs):
        course_id = int(self.kwargs['course_id'])
        reload = request.GET.get('reload', False) == "True"
        existing_records = self.model.objects.filter(assignment__course__course_id = course_id).first()
        
        if existing_records is None or reload:
            api = CanvasAPI()

            course = CanvasCourse.objects.filter(course_id = course_id).first()
            
            # Delete existing data
            self.model.objects.filter(assignment__course = course).all().delete()
            Assignment.objects.filter(course = course).all().delete()
            StudentCourse.objects.filter(course = course).all().delete()
             
            json_data = api.get_assignments(course_id)
            json_list = list(json_data) #the data from canvas
            
            for assignment in json_list:   #get the stuff i need from the canvas data
                assignment_id = assignment['id']
                assignment_name = assignment['name']             
                has_override = assignment['has_overrides']
                is_quiz = assignment['is_quiz_assignment']  
                 
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
                
                Assignment.user_objects.create(assignment_id = assignment_id, name = assignment_name, start_date = start_date, due_date = due_date, end_date = end_date, has_override = has_override, is_quiz = is_quiz, course = course)
            
            student_list = api.get_students(course_id)
            for student in student_list:
                localstudent = Student.objects.filter(canvas_id = int(student['id'])).first()
                if localstudent is not None:
                    StudentCourse.user_objects.create(student = localstudent, course = course) 
            
            json_data = api.get_submissions(course_id)
            json_list = list(json_data) #the data from canvas
            
            for sub in json_list:
                student_id = sub['user_id']
                student = Student.objects.filter(canvas_id = student_id).first()
                
                assignment_id = sub['assignment_id']
                assignment = Assignment.objects.filter(assignment_id = assignment_id).first()
                
                submitted = False
                if sub['workflow_state'] != 'unsubmitted':
                    submitted = True
                late = sub['late']
                self.model.user_objects.create(student = student, assignment = assignment, submitted = submitted, late = late)
        
        return super(SubmissionListView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super(SubmissionListView, self).get_context_data(*args, **kwargs) 
        course_id = int(self.kwargs['course_id'])
        current_date = datetime.now()
        
        last_past_assignment = Assignment.objects.filter(course__course_id = course_id, due_date__lte=current_date  ).order_by('-due_date', '-name').first()
        load_date = Submission.objects.filter(assignment__course__course_id = course_id).order_by('created_at').first()
        if load_date is not None:
            context['load_date'] = load_date
            context['current_date'] = current_date
            
            assignment_list = Assignment.objects.filter(course__course_id = course_id).all().order_by('due_date', 'name').values()
            student_list = Student.objects.filter(studentcourse__course__course_id = course_id).all().order_by('sortable_name').values()
            
            submissions = []
            for student in student_list:
                temp = {}
                temp['student'] = student
                temp['assignments'] = []
                for index, assignment in enumerate(assignment_list):
                    temp2 = list(Submission.objects.filter(student__canvas_id = student['canvas_id'], assignment__assignment_id = assignment['assignment_id']).values())
                    
                    if temp2:
                        temp2 = temp2.pop()
                        if last_past_assignment and temp2['assignment_id'] == last_past_assignment.id:
                            temp2['latest_assignment'] = True
                            assignment_list[index]['latest_assignment'] = True
                        temp['assignments'].append(temp2)
                    else:
                        temp['assignments'].append({})
                submissions.append(temp)
            
            context['assignments'] = assignment_list
            context['submissions'] = submissions
        
        return context
    
    def get_queryset(self):
        return self.model.objects.all().order_by('student_id' , 'assignment_id')
    
    
class PACSCourseRotation(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['faculty_tools', 'course_rotation']
    template_name = 'course_rotation.html'
    page_title = 'PACS Course Rotation'    
    
class PACSCourseSME(CurrentUserMixin,CCETemplateView):
    sidebar_group = ['faculty_tools', 'course_sme']
    template_name = 'course_sme.html'
    page_title = 'PACS Course SME'   
    