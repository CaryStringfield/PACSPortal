"""cls URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings

from django.contrib import admin

from django.conf.urls import include, url
from django.conf.urls.static import static


urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
              + [
                    url(r'^admin/', include(admin.site.urls)),
                  
                    url(r'^st/', include("staff_tools.urls")),
                  
                    # Faculty Tools                 
                    url(r'^ft/', include("faculty_tools.urls")),

                    # Canvas Lists
                    url(r'^c/', include("canvas.urls")),
                  
                    # Apps for development purposes only.
                    #    Should be commented out before commited
                    
                    # Sample CCE-IT Toolkit apps
                    url(r'^p/', include("tasks.urls")),
                    url(r'^b/', include("boards.urls")),

                     
                    # Default 
                    url(r'', include("staff_resources.urls")),
              ]

