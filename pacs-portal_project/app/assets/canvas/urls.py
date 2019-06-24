# Django imports
from django.conf.urls import url, include

# Nucleus imports
from nucleus.decorators import is_admin, is_member

# View imports
from canvas.views import AdminCourseListView, CourseListView, StudentListView, SubaccountListView, TermListView
from canvas.views import AssignmentListView, StudentCourseListView

urlpatterns = [

    url(r'^course/$', is_member(CourseListView.as_view(), ["PACSATAdvising"]),
        name='canvas_course_list'),

    url(r'^admincourse/$', is_admin(AdminCourseListView.as_view()),
        name='canvas_admincourse_list'),

    url(r'^student/$', is_admin(StudentListView.as_view()),
        name='canvas_student_list'),

    url(r'^studentcourse/', include([
        url(r'^(?P<course_id>\d+)/$', is_admin(StudentCourseListView.as_view()),
            name='canvas_studentcourse_list_course_id'),
        url(r'$', is_admin(StudentCourseListView.as_view()),
            name='canvas_studentcourse_list'),   
    ])),
        
    url(r'^assignment/', include([
        url(r'^(?P<course_id>\d+)/$', is_admin(AssignmentListView.as_view()),
            name='canvas_assignment_list_course_id'),
        url(r'$', is_admin(AssignmentListView.as_view()),
            name='canvas_assignment_list'),   
    ])),
                                           

    url(r'^subaccount/$', is_admin(SubaccountListView.as_view()),
        name='canvas_subaccount_list'),

    url(r'^term/$', is_admin(TermListView.as_view()),
        name='canvas_term_list'),

    ]

