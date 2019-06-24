# Django imports
from django.conf.urls import url, include

# Nucleus imports
from nucleus.decorators import is_admin, is_member

# View imports
from faculty_tools.views import PACSCourseRotation, PACSCourseSME, CourseListView, EditDueDates, AssignmentListView, StudentListView, SubmissionListView
from canvas.views import CourseListView as CanvasCourseListView

urlpatterns = [

    url(r'^course_rotation', is_member(PACSCourseRotation.as_view(), ["PACSATAdvising"]), name="course_rotation"),
    url(r'^course_sme', is_member(PACSCourseSME.as_view(), ["PACSATAdvising"]), name="course_sme"),

    url(r'^course_list/', include([
        url(r'^(?P<course_id>\d+)/', include([
            url(r'^edit/$', is_member(EditDueDates.as_view(), "Faculty"),
                name='edit_due_dates'),
        ])),
        url(r'^(?P<course_id>\d+)/', include([
            url(r'^extend/$', is_member(AssignmentListView.as_view(), "Faculty"), 
                name='assignment_list'),
            url(r'^(?P<assignment_id>\d+)/', include([
                url(r'^extend/$', is_member(StudentListView.as_view(), "Faculty"),
                    name='student_list'),
                url(r'^(?P<student_id>\d+)/', include([
                    url(r'^extend/$', is_member(EditDueDates.as_view(), "Faculty"),
                        name='extend_dates'),
                ])),
            ]))
        ])), 
        url(r'^(?P<course_id>\d+)/', include([
            url(r'^submissions/$', is_member(SubmissionListView.as_view(), "Faculty"),
                name='view_submissions'),
        ])),
        url(r'',is_member(CourseListView.as_view(), "Faculty"),
            name='course_list', ),
    ])),
               

    url(r'^canvas_course_list/', include([ 
        url(r'^(?P<course_id>\d+)/', include([
            url(r'^submissions/$', is_member(SubmissionListView.as_view(), "PACSATAdvising"),
                name='view_submissions'),
        ])),
        url(r'', is_member(CanvasCourseListView.as_view(), "PACSATAdvising"),
            name='canvas_course_list'),
    ])),

       
    ]

