from django.conf.urls import url, include

from tasks.views import TaskCreateView, TaskUpdateView, TaskDeleteView, \
    TaskDetailView, TaskListView, TaskStatusUpdateView, CompletedTaskListView

from nucleus.decorators import is_admin

urlpatterns = [
        url(r'^(?P<pk>\d+)/', include([
            url(r'^edit/$', is_admin(TaskUpdateView.as_view()),
                name='edit_task'),
            url(r'^update_status/$',
                is_admin(TaskStatusUpdateView.as_view()),
                name='update_task_status'),
            url(r'^delete/$', is_admin(TaskDeleteView.as_view()),
                name='delete_task'),
            url(r'^$', is_admin(TaskDetailView.as_view()),
                name='view_task'),
        ])),
        url(r'^add/', is_admin(TaskCreateView.as_view()),
            name='add_task'),
        url(r'^completed/', is_admin(CompletedTaskListView.as_view()),
            name='browse_completed_tasks'),
        url(r'^$', is_admin(TaskListView.as_view())
            , name='browse_tasks'),
]
