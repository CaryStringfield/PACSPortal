from django.conf.urls import url, include

from boards.views import BoardUpdateView, BoardDeleteView, BoardCreateView, \
    BoardListView

from nucleus.decorators import is_admin

urlpatterns = [

    #url(r'^b/', include([
    url(r'^(?P<pk>\d+)/', include([
        url(r'^edit/$', is_admin(BoardUpdateView.as_view()),
            name='edit_board'),
        url(r'^delete/$', is_admin(BoardDeleteView.as_view()),
            name='delete_board'),
    ])),
    url(r'^create_board/', is_admin(BoardCreateView.as_view()),
        name='add_board', ),
    url(r'', is_admin(BoardListView.as_view()),
        name='browse_boards', ),
    #url(r'', login_required(DashboardView.as_view()),
    #    name='dashboard', ),
]
