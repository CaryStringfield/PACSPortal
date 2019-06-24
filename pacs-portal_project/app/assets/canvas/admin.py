from toolkit.helpers.admin import auto_admin_register
from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect

# Nucleus Imports
from nucleus.api import CanvasAPI
from nucleus.auth import UserCredentials 
from nucleus import settings

# Model Imports
from models import Subaccount, Course, Term, Student
from faculty_tools.models import Submission, StudentCourse, Assignment

class TermAdmin(admin.ModelAdmin):
    list_display = ('term_id', 'name')


class SubaccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'subaccount_id', 'parent')
    change_list_template = 'admin/subaccount_change_list.html'
    
    def get_urls(self):
        super_urls = super(SubaccountAdmin, self).get_urls()
        custom_urls = [
            url('reload/$', self.reload_subaccounts)
        ]
        return custom_urls + super_urls
    
    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        most_recent_timestamp = self.model.objects.all().order_by('created_at').first()
        if most_recent_timestamp is not None:
            extra_context['load_date'] = most_recent_timestamp.created_at
        return super(SubaccountAdmin, self).changelist_view(request, extra_context=extra_context)
    
    def reload_subaccounts(self, request):
        self.model.objects.all().delete()
        creds = UserCredentials()
        api = CanvasAPI()
        
        first_iteration = api.get_subaccounts()
        for sub_account in first_iteration:
            sub_account_create = self.model.objects.create(subaccount_id = sub_account['id'], name = sub_account['name'])
            sub_account_create.save()
    
        second_iteration = api.get_subaccounts()
        for sub_account in second_iteration:
            sub_account_parent = self.model.objects.filter(subaccount_id = sub_account['parent_account_id']).first()
            sub_account_child = self.model.objects.filter(subaccount_id = sub_account['id']).first()
            sub_account_child.parent = sub_account_parent
            sub_account_child.save()
            
        self.message_user(request, "Subaccounts successfully reloaded!")
        return HttpResponseRedirect("../")


class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_code', 'course_id', 'subaccount']
    change_list_template = 'admin/course_change_list.html'
    
    def get_urls(self):
        super_urls = super(CourseAdmin, self).get_urls()
        custom_urls = [
            url(r'(?P<term_id>.+)/reload/$', self.reload_course)
        ]
        return custom_urls + super_urls

    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        most_recent_timestamp = self.model.objects.all().order_by('created_at').first()
        if most_recent_timestamp is not None:
            extra_context['load_date'] = most_recent_timestamp.created_at
        extra_context['terms'] = Term.objects.all()
        extra_context['current_term_id'] = settings.CURRENT_TERM
        return super(CourseAdmin, self).changelist_view(request, extra_context = extra_context)

    def reload_course(self, request, term_id):
        term = Term.objects.filter(term_id = term_id).first()        
        self.model.objects.filter(term = term).delete()
        creds = UserCredentials()
        api = CanvasAPI(term = term_id)
        
        course_list = api.get_courses_by_term()
        for course in course_list:
            subaccount = Subaccount.objects.filter(subaccount_id = course['account_id']).first()
            course_create = self.model.objects.create(course_id = course['id'], name = course['name'], course_code = course['course_code'], term = term, subaccount = subaccount)
            course_create.save()
            
        self.message_user(request, "Course list successfully reloaded!")
        return HttpResponseRedirect("../../")
    
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'login_id', 'canvas_id', 'sis_user_id']
    change_list_template = 'admin/student_change_list.html'
    
    def get_urls(self):
        super_urls = super(StudentAdmin, self).get_urls()
        custom_urls = [
            url(r'reload/$', self.reload_student)
        ]
        return custom_urls + super_urls

    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        most_recent_timestamp = self.model.objects.all().order_by('created_at').first()
        if most_recent_timestamp is not None:
            extra_context['load_date'] = most_recent_timestamp.created_at
        return super(StudentAdmin, self).changelist_view(request, extra_context=extra_context)

    def reload_student(self, request):
        self.model.objects.all().delete()
        Submission.objects.all().delete()
        creds = UserCredentials()
        api = CanvasAPI()
        
        student_list = api.get_account_users()
        for student in student_list:
            student_create = self.model.objects.create(canvas_id = student['id'], name = student['name'], sortable_name = student['sortable_name'], short_name = student['short_name'], sis_user_id = student['sis_user_id'], login_id = student['login_id']) 
            student_create.save()
            
        self.message_user(request, "Student list successfully reloaded!")
        return HttpResponseRedirect("../")


admin.site.site_header = "Pacs-Portal Admin Panel"

admin.site.register(Subaccount, SubaccountAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Term, TermAdmin)    
admin.site.register(Student, StudentAdmin)
