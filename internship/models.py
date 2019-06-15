from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    dept_code = models.CharField('Department code', max_length=50, primary_key=True)
    dept_name = models.CharField('Department name', max_length=50)
    
    def __str__(self):
         return '(%s) %s'%(self.dept_code, self.name)
     
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
    admission_year = models.DateField( auto_now=False)

    def __str__(self):
        return '(%s) %s'%(self.adm_no, self.full_name)


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
    
    
class AllocatedSupervisor(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    
class Application(models.Model):
    organization = models.CharField( max_length=50)
    location = models.CharField(max_length=50)
    branch = models.CharField(blank=True, null=True, max_length=50)
    PO_BOX = models.CharField('P.O BOX',null = True, blank=True, max_length=50)
    status = models.CharField( max_length=50, default = 'pending')
    application_date = models.DateField(auto_now=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    
class Organization(models.Model):
    organization = models.CharField( max_length=50)
    county = models.CharField( max_length=50)
    town = models.CharField(max_length=50)
    building = models.CharField( max_length=50)
    industrial_supervisor = models.CharField(max_length=50)
    start_date = models.DateField(auto_now=False)
    
    
class Logbook(models.Model):
    date = models.DateField(auto_now=False)
    work_done = models.TextField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    
    
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='recipient', on_delete=models.CASCADE)
    message_content = models.TextField()
    sent_on = models.DateTimeField(auto_now=True)
    read_status = models.BooleanField(default=False)