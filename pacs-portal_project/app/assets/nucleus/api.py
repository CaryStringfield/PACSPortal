__author__ = 'Will Poillion & Cary Stringfield'

import itertools
import requests
import logging

from nucleus import settings

class GroupSetBuilder():
    def __init__(self):
        """Construct a set of groups"""
        self.groups = {}

    def add_group_member(self, user_id, group_id):
        if group_id not in self.groups:
            self.groups[group_id] = [user_id]
        else:
            self.groups[group_id].append(user_id)


class CanvasAPI():
    
    def __init__(self, sub_account = None, term = None, debug = None):
        """Construct an object to access the Canvas API. """
        self.access_token = settings.CANVAS_TOKEN
        self.api_url = settings.CANVAS_URL + settings.CANVAS_API_PREFIX
        
        if debug is not None:
            self.DEBUG = debug
        else:
            self.DEBUG = settings.DEBUG
        self.DEBUG = False
        
        if sub_account is not None:
            self.SUB_ACCOUNT = sub_account
        else:
            self.SUB_ACCOUNT = settings.PACS_SUBACCOUNT
            
        if term is not None:
            self.TERM = term
        else:
            self.TERM = settings.CURRENT_TERM


    def put(self, api_url, payload=None):
        url = self.api_url + api_url

        if payload is None:
            payload = {}

        if self.access_token is not None:
            payload['access_token'] = self.access_token

        r = requests.put(url, params=payload)
        # raises an exception if there was an http error
        r.raise_for_status()
        
        if self.DEBUG:
            logging.warning("CanvasAPI Put: " + url)
            logging.warning("CanvasAPI Put Payload: " + str(payload))
            logging.warning("CanvasAPI Put Result: " + str(list(r)))
        
        return r


    def post(self, api_url, payload=None):
        url = self.api_url + api_url

        if payload is None:
            payload = {}

        if self.access_token is not None:
            payload['access_token'] = self.access_token

        r = requests.post(url, data=payload)
        # raises an exception if there was an http error
        r.raise_for_status()
        
        if self.DEBUG:
            logging.warning("CanvasAPI Post: " + url)
            logging.warning("CanvasAPI Post Payload: " + str(payload))
            logging.warning("CanvasAPI Post Result: " + str(list(r)))
        
        return r
    
    def delete(self, api_url, payload=None):
        url = self.api_url + api_url

        if payload is None:
            payload = {}

        if self.access_token is not None:
            payload['access_token'] = self.access_token

        r = requests.delete(url, params=payload)
        # raises an exception if there was an http error
        r.raise_for_status()
        
        if self.DEBUG:
            logging.warning("CanvasAPI Delete: " + url)
            logging.warning("CanvasAPI Delete Payload: " + str(payload))
            logging.warning("CanvasAPI Delete Result: " + str(list(r)))
        
        return r
    
    def get_response(self, url, payload=None):
        if payload is None:
            payload = {}

        if self.access_token is not None:
            payload['access_token'] = self.access_token

        r = requests.get(url, params=payload)
        # raises an exception if there was an http error
        r.raise_for_status()
        
        if self.DEBUG:
            logging.warning("CanvasAPI Get: " + url)
            logging.warning("CanvasAPI Get Payload: " + str(payload))
            logging.warning("CanvasAPI Get Result: " + str(list(r)))
        
        return r


    def get_responses(self, api, payload=None):
        url = self.api_url + api

        print url
        responses = []
        while True:

            r = self.get_response(url, payload)
            responses.append(r)

            if 'next' in r.links:
                url = r.links['next']['url']
            else:
                break

        if self.DEBUG:
            logging.warning("CanvasAPI Get: " + url)
            logging.warning("CanvasAPI Get Payload: " + str(payload))
            logging.warning("CanvasAPI Get Result: " + str(list(responses)))

        return responses


    def get(self, api, to_json=True, payload=None, single=False):
        
        logging.basicConfig()

        responses = self.get_responses(api, payload=payload)
        if to_json:
            responses = [r.json() for r in responses]

        if single:
            # print responses
            return responses[0]
        else:
            # print responses
            return (reduce(lambda x, y: itertools.chain(x, y), responses))
        
        
    def get_canvasID(self, OUNetID):
        api_response = self.get('/accounts/%s/users?search_term=%s' % (self.SUB_ACCOUNT, OUNetID), single=True)
        canvasID = None
        for user in api_response:
            canvasID = user['id']
        return canvasID
    
    def get_class_by_teacher(self, canvasID):
        return self.get('/accounts/%s/courses?published=true&by_teachers[]=%s&enrollment_term_id=%s' % (self.SUB_ACCOUNT, canvasID, self.TERM))

    def get_user(self, user_id):
        return self.get('/users/%s/profile' % user_id, single=True)

    def get_users(self, course_id):
        return self.get('/courses/%s/users' % course_id)

    def get_group_membership(self, group_id):
        return self.get('/groups/%s/memberships' % group_id)

    def get_courses(self, course_id):
        return self.get('/courses/%s' % course_id)

    def get_course_groups(self, course_id):
        return self.get('/courses/%s/groups' % course_id)

    def get_assignment(self, course_id, assignment_id, override_assignment_dates = False):
        if override_assignment_dates:
            result = self.get('/courses/%s/assignments/%s?override_assignment_dates=true' % (course_id, assignment_id), single=True)    
        else:
            result = self.get('/courses/%s/assignments/%s?override_assignment_dates=false' % (course_id, assignment_id), single=True) 
        return result    
    
    def get_submissions(self, course_id):
        return self.get('/courses/%s/students/submissions?student_ids[]=all' % (course_id))   

    def get_assignments(self, course_id, override_assignment_dates = False):
        if override_assignment_dates:
            result = self.get('/courses/%s/assignments?override_assignment_dates=true' % course_id)
        else:
            result = self.get('/courses/%s/assignments?override_assignment_dates=false' % course_id) 
        return result
    
    def get_students(self, course_id):
        return self.get('/courses/%s/students' % course_id)

    def get_account_users(self):
        return self.get('/accounts/%s/users' % self.SUB_ACCOUNT)

    def get_course_enrollments(self, course_id):
        return self.get('/courses/%s/enrollments' % course_id)

    def is_teacher_of_course(self, course_id, ounet_id ):
        result = False
        canvasID = self.get_canvasID(ounet_id)
        courses = self.get_class_by_teacher(canvasID)
        for course in courses:
            if int(course_id) == int(course['id']):
                result = True
        return result
    
    def update_assignment_dates(self, course_id, assignment_id, due_date, start_date, end_date ):
        url = "/courses/" + str(course_id) + "/assignments/" + str(assignment_id)
        payload = {'assignment[due_at]':due_date, 'assignment[unlock_at]':start_date, 'assignment[lock_at]':end_date}
        return self.put(url, payload)
    
    def get_assignment_overrides(self, course_id, assignment_id):
        return self.get('/courses/%s/assignments/%s/overrides' % (course_id, assignment_id))

    def create_assignment_override(self, course_id, assignment_id, student_id, due_date, start_date, end_date  ):
        url = "/courses/" + str(course_id) + "/assignments/" + assignment_id + "/overrides"
        payload = {'assignment_override[student_ids][]': str(student_id), 'assignment_override[due_at]':due_date, 'assignment_override[unlock_at]':start_date, 'assignment_override[lock_at]':end_date }
        return self.post(url, payload)

    def delete_assignment_overrides(self, course_id, assignment_id):
        override_list = self.get('/courses/%s/assignments/%s/overrides' % (course_id, assignment_id))
        for override in override_list:
            delete = self.delete('/courses/%s/assignments/%s/overrides/%s' % (course_id, assignment_id, override['id']))
        return

    def get_assignment_override(self, course_id, assignment_id, student_id):
        overrides = self.get_assignment_overrides(course_id, assignment_id)
        result = False
        for override in overrides:
            student_ids = override['student_ids']
            if int(student_id) in student_ids:
                result = override
        return result

    def update_assignment_override(self, course_id, assignment_id, student_id, due_date, start_date, end_date):
        override = self.get_assignment_override(course_id, assignment_id, student_id)
        url = "/courses/" + str(course_id) + "/assignments/" + str(assignment_id) + "/overrides/" + str(override['id'])
        payload = {'assignment_override[due_at]': due_date, 'assignment_override[unlock_at]': start_date, 'assignment_override[lock_at]': end_date}
        return self.put(url, payload)

    def get_subaccounts(self, account_id = None):
        if account_id is None:
            account_id = self.SUB_ACCOUNT
        sub_accounts = self.get('/accounts/%s/sub_accounts?recursive=true' % account_id)
        return sub_accounts

    def get_courses_by_term(self, term = None, account = None):
        if term is None:
            term = self.TERM
        if account is None:
            account = self.SUB_ACCOUNT
        return self.get('/accounts/%s/courses?enrollment_term_id=%s' % (account, term))









    def get_quiz_submissions(self, course_id, quiz_id):
        return self.get(
            '/courses/%s/quizzes/%s/submissions' % (course_id, quiz_id))


    def get_assignment_submissions(self, course_id, assignment_id,
                                   grouped=False):
        """
        Only returns those submissions that have actually been submitted, rather than potential submissions.
        :param course_id:
        :param assignment_id:
        :return:
        """
        payload = {'grouped': grouped}
        submissions = self.get('/courses/%s/assignments/%s/submissions' % (
        course_id, assignment_id), payload=payload)
        return filter(lambda sub: sub['workflow_state'] != 'unsubmitted',
                      submissions)


    def grade_assignment_submission(self, course_id, assignment_id, user_id,
                                    grade, comment=None):

        payload = {'grade_data[%s][posted_grade]' % user_id: grade}
        if comment is not None:
            payload['grade_data[%s][text_comment]' % user_id] = comment

        return self.post(
            '/courses/%s/assignments/%s/submissions/update_grades' % (
            course_id, assignment_id), payload=payload)


    def comment_assignment_submission(self, course_id, assignment_id, user_id,
                                      comment):

        payload = {'grade_data[%s][text_comment]' % user_id: comment}

        return self.post(
            '/courses/%s/assignments/%s/submissions/update_grades' % (
            course_id, assignment_id), payload=payload)


    def set_group_name(self, group_id, name):

        payload = {'name': name}
        return self.put('/groups/%s' % (group_id), payload=payload)


    def set_group_membership(self, group_set_builder):
        results = []
        for group_id, membership in group_set_builder.groups.iteritems():
            payload = {}
            payload['members[]'] = membership
            # print payload
            self.put('/groups/%s' % (group_id), payload=payload)
            # return results


    def get_submission_attachments(self, submission, as_bytes=False):
        """
        Get a dictionary containing the attachment files for this submission.
        :param submission: A JSON submission object.
        :param as_bytes: If True, get the file as bytes, else it will be returned as text.
        :return: A dictionary mapping filename to file contents.
        """
        attachments = {}

        if 'attachments' in submission:
            for attachment in submission['attachments']:
                r = requests.get(attachment['url'],
                                 params={'access_token': self.access_token})
                if as_bytes:
                    attachments[attachment['filename']] = r.content
                else:
                    attachments[attachment['filename']] = r.text
        return attachments
    
    
    
    

