# Django imports
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models

# Nucleus imports
from nucleus.models import PACSModel
from canvas.models import Student, Course as CanvasCourse

class Assignment(PACSModel):
    assignment_id = models.IntegerField(unique = True)
    name = models.CharField(max_length = 500, null=True)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    has_override = models.BooleanField(default = False)
    is_quiz = models.BooleanField(default = False)
    course  = models.ForeignKey(CanvasCourse, on_delete=models.CASCADE,)
    
    def _str_(self):
        return self.assignment_id, self.name, self.start_date, self.due_date, self.end_date, self.has_override, self.is_quiz

    def __unicode__(self):
        return u'{0}'.format(self.name)
        
    def get(self):
        return self.assignment_id
    
class StudentCourse(PACSModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,)
    course = models.ForeignKey(CanvasCourse, on_delete=models.CASCADE,)

    class Meta:
        verbose_name_plural = "StudentCourses"
        ordering = ('student','course')

    def _str_(self):
        return self.student, self.course  
    
    def __unicode__(self):
        return u'{0}'.format(self.student)

    def get(self):
        return self.student
    
class Submission(PACSModel):
    student = models.ForeignKey(Student, null = True, on_delete=models.CASCADE,)
    assignment = models.ForeignKey(Assignment, null = True, on_delete=models.CASCADE,)
    submitted = models.BooleanField(default = False)
    late = models.BooleanField(default = False)
    
    def _str_(self):
        return self.student, self.assignment, self.submitted, self.late
    
    def __unicode__(self):
        return u'{0}'.format(self.student, self.assignment)
        
    def get(self):
        return self.student, self.assignment, self.submitted, self.late
    
    