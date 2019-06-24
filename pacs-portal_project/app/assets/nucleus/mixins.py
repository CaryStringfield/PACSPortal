import logging
from nucleus.auth import UserCredentials
from nucleus import settings


class CurrentUserMixin(object):
    
    
    def get_context_data(self, **kwargs):
        auth = UserCredentials()
        context = {}
        context =  super(CurrentUserMixin, self).get_context_data(**kwargs)
        context['user_full_name'] = auth.get_FirstName() + " " + auth.get_LastName()
        context['user_ounetid'] = auth.get_OUNetID()
        context['user_email'] = auth.get_Email()
        
        for membership in auth.MemberOf:
            context['user_is_' + str(membership.lower())] = True
            
        context['user_is_admin'] = auth.is_admin()
        context['user_groups'] = auth.MemberOf
        context['server_type'] = settings.SERVER_TYPE
        return context