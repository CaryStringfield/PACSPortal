from toolkit.helpers.admin import auto_admin_register
from models import Announcement
from django.contrib import admin

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'school', 'body')

admin.site.register(Announcement, AnnouncementAdmin)
    
#auto_admin_register(__package__, exclude=(Course.__name__, As