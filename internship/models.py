from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator

def current_year():
    return datetime.date.today().year


def max_value_current_year(value):
    return MaxValueValidator(current_year())(value)


class Department(models.Model):
    dept_code = models.CharField('Department code', max_length=50, primary_key=True)
    dept_name = models.CharField('Department name', max_length=50)
    
    def __str__(self):
         return '(%s) %s'%(self.dept_code, self.dept_name)
     
class Course(models.Model):
    course_code = models.CharField(max_length=50, primary_key=True)
    course_name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=True)

    def __str__(self):
        return '(%s) %s'%(self.course_code, self.course_name)


class Student(models.Model):
    adm = models.CharField(max_length=50, primary_key=True)
    full_name = models.CharField(max_length=200)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    admission_year =models.PositiveIntegerField(
        default=current_year(), validators=[MinValueValidator(1984), max_value_current_year])

    def __str__(self):
        return '(%s) %s'%(self.adm, self.full_name)


class Coordinator(models.Model):
    staff_no = models.CharField(max_length=50, primary_key=True)
    full_name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return '(%s) %s'%(self.staff_no, self.full_name)


class Supervisor(models.Model):
    staff_no = models.CharField(max_length=50, primary_key=True)
    full_name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return '(%s) %s'%(self.staff_no, self.full_name)
    

class AcademicYear(models.Model):
    year = models.CharField(max_length=50)
    semester = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=0)
    
    
class AllocatedSupervisor(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    department = models.ForeignKey(Department,default='', on_delete=models.CASCADE)
    
    def __str__(self):
        return '(%s) %s'%(self.supervisor, self.department)

    
class Application(models.Model):
    organization = models.CharField( max_length=50)
    branch = models.CharField(blank=True, null=True, max_length=50)
    PO_BOX = models.CharField('P.O BOX',null = True, blank=True, max_length=50)
    application_status =(
        ( 'P', 'Pending'),
        ( 'A', 'Awaiting'),
        ('F', 'Failed'),
        ('S', 'Successfull'),
    )
    status = models.CharField(max_length=50,choices=application_status, default='P')
    application_date = models.DateField(auto_now=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    
class Organization(models.Model):
    organization = models.CharField( max_length=50)
    county = models.CharField( max_length=50)
    town = models.CharField(max_length=50)
    building = models.CharField( max_length=50)
    industrial_supervisor = models.CharField(max_length=50)
    start_date = models.DateField(auto_now=False,
                                  validators=[MinValueValidator(2019), max_value_current_year])
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    def __str__(self):
        return '(%s) %s'%(self.student, self.organization)
    
    
class Logbook(models.Model):
    week = models.PositiveIntegerField()
    date = models.DateField(auto_now=True)
    work_done = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    
class Message(models.Model):
    student = models.ForeignKey(Student,null=True, blank=True, on_delete=models.CASCADE)
    coordinator = models.ForeignKey(Coordinator,blank=True,null=True, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor,blank=True, null=True,  on_delete=models.CASCADE)
    message_content = models.TextField()
    outgoing = models.BooleanField(default=False)
    sent_on = models.DateTimeField(auto_now=True)
    read_status = models.BooleanField(default=False)
 
    # to enable convertion to Json
    # def as_dict(self):
    #     return {
    #         'student' : self.student,
    #         'coordinator' : self.coordinator,
    #         'supervisor' : self.supervisor,
    #         'message_content' : self.message_content,
    #         'sent_on' : self.sent_on,
    #         'read_status': self.read_status
    #     }
        
        
class Notification(models.Model):
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)


class Assessment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    department = models.ForeignKey(Department,default="", on_delete=models.CASCADE)
    date = models.DateField( auto_now=False, auto_now_add=False)

