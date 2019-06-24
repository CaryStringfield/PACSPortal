from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from nucleus.decorators import is_admin, is_member

from staff_tools.views import CropTool, ButtonMaker, BannerMaker

urlpatterns = [
	url(r'^crop_tool', is_member(CropTool.as_view(), "Staff"), name="crop_tool"),
	url(r'^button_maker', is_member(ButtonMaker.as_view(), "Staff"), name="button_maker"),
	url(r'^banner_maker', is_member(BannerMaker.as_view(), "Staff"), name="banner_maker"),
    
]