from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from nucleus.decorators import is_admin, is_member

# Views
from staff_resources.views import DashboardView, AnnouncementUpdateView, AnnouncementDeleteView, AnnouncementCreateView, AnnouncementDetailView
# Simple Pages 
from staff_resources.views import ObjectiveBuilder, CourseWorkloadEstimator, LearningOutcomeGenerator

urlpatterns = [
	url(r'^outcome-generator', is_member(LearningOutcomeGenerator.as_view(), ["Staff", "Faculty"]), name="outcome-generator"),
	url(r'^workload-estimator', is_member(CourseWorkloadEstimator.as_view(), ["Staff", "Faculty"]), name="workload-estimator"),
	url(r'^objective_builder', is_member(ObjectiveBuilder.as_view(), ["Staff", "Faculty"]), name="objective_builder"),
	
	url(r'^(?P<pk>\d+)/', include([
        url(r'^edit/$', is_member(AnnouncementUpdateView.as_view(), ["Faculty","Staff"]),
            name='edit_announcement'),
        url(r'^delete/$', is_member(AnnouncementDeleteView.as_view(), ["Faculty","Staff"]),
            name='delete_announcement'),	
		url(r'^$', AnnouncementDetailView.as_view(),
			name='view_announcement'),		   
    ])),
    url(r'^create/', is_member(AnnouncementCreateView.as_view(), ["Faculty","Staff"]),
        name='add_announcement', ),
   
    # DEFAULT    
    url(r'', DashboardView.as_view(), name="dashboard"),
    
]