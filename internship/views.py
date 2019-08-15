from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from django.views import View
from django.db.models import Q
from .models import Student, Coordinator, Course, Department, Message, Application,Organization, Logbook, AcademicYear, AllocatedSupervisor, Notification, Supervisor, Assessment
from . import forms
# import utils for creating pdf
from .utils import render_to_pdf

from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
import datetime
import json
# from . import forms

# Create your views here.

class Index(View):
    template = 'index.html'
    
    def get(self, request):
        return render(request,self.template)
    
class Login(View):
    template = 'login.html'
    form = forms.LoginForm
    
    def get(self, request):
        if request.user.is_authenticated:
            username = request.user
            student = Student.objects.filter(adm=username).exists()
            coordinator = Coordinator.objects.filter(staff_no=username).exists()
            if student:
                return redirect('applicationStatus')
            elif coordinator:
                return redirect('coordinatorIndex')
            else:
                return redirect('admin')
        else:
            form = self.form(None)
            return render(request, self.template, {'form': form})
    
    def post(self, request):
        form = self.form(request.POST)
        
        # get username passed from form
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            login(request, user)
            # query each model
            student = Student.objects.filter(adm=username).exists()
            coordinator = Coordinator.objects.filter(staff_no=username).exists()
            supervisor = Supervisor.objects.filter(staff_no=username).exists()
            # redirect to appropriate portal
            if student:
                return redirect('studentIndex')
            elif coordinator:
                return redirect('coordinatorIndex')
            elif supervisor:
                return redirect('supervisorIndex')
        else:
            context ={
                'form': self.form(request.POST),
                'errors': 'Either username or password is wrong'               
            }
            return render(request, self.template, context)
            

class Logout(View):
    template = 'index.html'
    
    def get(self, request):
        logout(request)
        return render(request, self.template)
        
class Register(View):
    template = 'register.html'
    form = forms.RegisterForm
    
    def get(self, request):
        return render(request, self.template, { 'form' : self.form })
        
    def post(self, request):
        form = self.form(request.POST)
        print('not validated')
        if form.is_valid():
            print('validated')
            username = form.cleaned_data['username']
            
            # check who the user is
            student = Student.objects.filter(adm=username).exists()
            coordinator = Coordinator.objects.filter(staff_no=username) .exists()
            supervisor = Supervisor.objects.filter(staff_no=username) .exists()
            
            if student or coordinator or supervisor:
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                # check if user has an account
                user_exists = User.objects.filter(username=username).exists()
                if user_exists:
                    context = {
                        'form' : self.form(request.POST),
                        'errors': 'this admission number or staff number is already registered'
                    }
                    return render(request, self.template, context)
                
                # register new user
                register_user = User.objects.create_user(username, email, password)
                register_user.save()
                
                
                messages.success(request,'Account has been successfully created')
                return redirect('login')
            
            else:
                context = {
                    'form' : self.form(request.POST),
                    'errors' : 'You do not exists in the university database.\r\n contact admin Please'
                }
                return render(request,self.template, context)
        else:
            context = {
                'form' : self.form(request.POST),
                'errors' : 'User already exists'
            }
            return render(request, self.template, context)
        
        
class Help(View):
    template = 'help.html'
    
    def get(self,request):
        return render(request, self.template)
        
        
class About(View):
    template = 'about.html'
    
    def get(self,request):
        return render(request, self.template)
        
   
        # students views/logic
def std_unread_messages(user):
    student = Student.objects.get(adm=user)
    unread_msg = Message.objects.filter(student=student).filter(outgoing=True).filter(read_status=False).count()
    if unread_msg==0:
        unread_msg=''
    return unread_msg
     
class StudentView(LoginRequiredMixin, UserPassesTestMixin, View):
    template = 'student/index.html'
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        return render(request,self.template)
    
class Apply(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    form = forms.ApplicationForm
    template = 'student/application.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
        
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        return render(request, self.template, { 'form':self.form,'unread_msg':unread_msg})
    
    def post(self, request):
        unread_msg = std_unread_messages(request.user)
        form = self.form(request.POST)
        if form.is_valid():
            student = Student.objects.get(adm=request.user)
            total_applications = Application.objects.filter(student=student).count()
            if total_applications < 3:
                instance = form.save(commit=False)
                instance.student = student
                instance.save()
                context ={
                    'form' : form,
                    'success' :  'Your application has been successfully sent',
                    'unread_msg': unread_msg,
                }
            else:
                context = {
                    'form': self.form(None),
                    'failed' : 'You can only apply for a maximum of 3 organizations please' 
                }
            return render(request, self.template, context)
        else:
            print(form)
            return render(request, self.template, {'form' : form})
        
    
class ApplicationStatus(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/application-status.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
        
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        user = self.request.user
        student =Student.objects.get(adm=user)
        applications = Application.objects.filter(student= student)
        return render(request, self.template, {'applications' : applications, 'unread_msg':unread_msg })
         
    
# fill logbook view
class FillLogbook(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/fill-logbook.html'
    form = forms.LogbookForm
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    date = datetime.date.today()
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        student = Student.objects.get(adm=request.user)
        check = Logbook.objects.filter(date=self.date).filter(student=student).exists()
        print(check)
        if not check:
            context ={
                'form': self.form
            }
        else:
            exists = 'Hey '+str(student.full_name)+'! You have already filled today`s work. Click update button to update details'
            logbook = Logbook.objects.filter(date=self.date).filter(student=student)
            for log in logbook:
                log_id = log.id    
            details = Logbook.objects.get(pk=log_id)
            context ={
                'form':self.form,
                'details': details,
                'entry_exists': exists,
                'unread_msg': unread_msg,
            }
        return render(request, self.template, context)
    
    def post(self, request):
        unread_msg = std_unread_messages(request.user)
        form = self.form(request.POST)
        student = Student.objects.get(adm=request.user)
        if form.is_valid():
            check = Logbook.objects.filter(date=self.date).filter(student=student).exists()
            if not check:
                instance = form.save(commit=False)
                instance.student = student
                instance.save()
                context ={
                        'form' : self.form(None),
                        'success' :  'details successfully filled in your logbook',
                        'unread_msg': unread_msg,
                }
            else:
                a = Logbook.objects.get(pk=request.POST['id'])
                form = self.form(request.POST, instance=a)
                form.save(commit=False)
                form.student = student
                form.save()
                messages.success(request,'Activities successfully updated \U0001F44F \U0001F44F')
                return redirect('logbook')
        else:
            print(self.form(request.POST))
            context = {
                'form': self.form(request.POST),
            }            
        return render(request, self.template, context)
    
    
    
class ViewLogbook(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/view-logbook.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
        
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        user= self.request.user
        student = Student.objects.get(adm = user)
        logbook = Logbook.objects.filter(student=student)
        print(logbook)
        logbook_details = {
        }
        for detail in logbook:
            print(detail.week,detail.work_done, detail.date) 
                
            logbook_details = Logbook.objects.filter(student=student)
            context ={
                'logbook' : logbook_details,
                'unread_msg':unread_msg,
            }
            print(logbook_details)
            # try:
            #     logbook_details[str(detail.week)]['date']=[].append(detail.date)
            #     logbook_details[str(detail.week)]['work_done'].append(detail.work_done)
            # except KeyError:
            #     logbook_details[str(detail.week)]['date'] = [detail.date,]
            #     logbook_details[str(detail.week)]['week_done'] = [detail.work_done]

        
        return render(request, self.template, context)
        
    
class LogbookPDF(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'student/logbook-pdf.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        user = self.request.user
        student = Student.objects.get(adm=user)
        logbook_details = Logbook.objects.filter(student=student)
        context ={
            'student' : student,
            'logbook' : logbook_details
        }
        pdf = render_to_pdf('student/logbook-pdf.html', context)
        return HttpResponse(pdf, content_type='application/pdf')
    
class LogbookGuidelines(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'student/logbook-guidelines.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        return render(request, self.template)
    
    
class FinalReportGuidelines(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'student/final-report.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        return render(request, self.template, {'unread_msg':unread_msg})
    
    
class OrganizationView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/organization.html'
    form = forms.OrganizationForm
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        student = Student.objects.get(adm=request.user)
        check = Organization.objects.filter(student=student).exists()
        if not check:
            return render(request, self.template)
        else:
            check = Organization.objects.get(student=student)
            print(check)         
            context = {
                'org': check.organization,
                'county': check.county,
                'town': check.town,
                'start': check.start_date,
                'building': check.building,
                'supervisor': check.industrial_supervisor,
                'unread_msg':unread_msg
                
            }
            return render(request, self.template, context)
        
    def post(self, request):
        org = request.POST['organization']
        county = request.POST['county']
        town = request.POST['town']
        start_date = request.POST['start']
        building = request.POST['building']
        supervisor = request.POST['supervisor']
        student = Student.objects.get(adm=request.user)
        check = Organization.objects.filter(student=student)
        if not check:
            instance = Organization(organization=org,county=county,town=town,
                                    start_date=start_date,building=building,industrial_supervisor=supervisor,student=student)
            instance.save()
            # context ={
            #         'success' :  'detail successfully saved'
            # }
            return redirect('organization')
        else:
            student = Student.objects.get(adm=request.user)
            instance = Organization.objects.get(student=student)
            instance.organization = org
            instance.county = county
            instance.town = town
            instance.start_date = start_date
            instance.building = building
            instance.industrial_supervisor = supervisor
            instance.save()
            return redirect('organization')
        return render(request, self.template, context)
    
    
class StudentNotification(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/notifications.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self,request):
        unread_msg = std_unread_messages(request.user)
        student = Student.objects.get(adm=request.user)
        print(student.course_code)
        course = Course.objects.get(course_code=student.course_code.course_code)
        notifications = Notification.objects.filter(department=course.department)

        return render(request, self.template,  {'notifications': notifications,'unread_msg': unread_msg})
    
    
    
class StudentMessages(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/messages.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        unread_msg = std_unread_messages(request.user)
        student = Student.objects.get(adm=request.user)
        msg_s = Message.objects.filter(student=student).exclude(supervisor = None).order_by('-sent_on')
        msg_c = Message.objects.filter(student=student).exclude(coordinator = None).order_by('-sent_on')
        course = Course.objects.get(course_code=student.course_code.course_code)
        coordinator = Coordinator.objects.get(department=course.department)
        supervisors = Supervisor.objects.filter(department=course.department)
        receiver ={}
        print(msg_s)
        for i in supervisors:
            receiver[str(i.staff_no)] ={
                'name': i.full_name,
            }
        receiver = json.dumps(receiver)
        context = {
            'receiver': receiver,
            'coordinator':coordinator,
            'messages_s' : msg_s,
            'messages_c' : msg_c,
            'unread_msg':unread_msg,
        }
        return render(request, self.template, context)
    
    
class ViewMessages(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/view-messages.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request,adm):
        sender=''
        student = Student.objects.get(adm=request.user)
        check_sup = Supervisor.objects.filter(staff_no=adm).exists()
        check_coord = Coordinator.objects.filter(staff_no=adm).exists()
        if check_sup:
            sup = Supervisor.objects.get(staff_no=adm)
            sender =sup
            update_msg =Message.objects.filter(student=student).filter(outgoing=True).filter(supervisor=sup)
            messages =Message.objects.filter(student=student).filter(supervisor=sup)
        if check_coord:
            coord = Coordinator.objects.get(staff_no=adm)
            sender = coord
            update_msg = Message.objects.filter(student=student).filter(outgoing=True).filter(coordinator=coord)
            messages = Message.objects.filter(student=student).filter(coordinator=coord)
            
        print(messages)
        # messages = Message.objects.filter(student=student)
        # update_msg = Message.objects.filter(student=student).filter(outgoing=True)
        for msg in update_msg:
            msg.read_status=True
            msg.save()
        unread_msg = std_unread_messages(request.user)
        # messages = JsonResponse(messages,safe=False)
        data = {}
        for msg in messages:
            time = msg.sent_on
            data[str(msg.id)] = {
                'student' : msg.student.full_name,
                'message_content' : msg.message_content,
                'time' : time.strftime("%b %d, %Y %H:%M"),
                'outgoing' : msg.outgoing
            }
        return render(request,self.template,{'messages': data,'sender': sender,'unread_msg':unread_msg})
    
    def post(self, request, adm):
        unread_msg = std_unread_messages(request.user)
        student = Student.objects.get(adm=request.user)
        coordinator = ''
        supervisor = ''
        student = Student.objects.get(adm=request.user)
        check_sup = Supervisor.objects.filter(staff_no=adm).exists()
        check_coord = Coordinator.objects.filter(staff_no=adm).exists()
        if check_sup:
            sup = Supervisor.objects.get(staff_no=adm)
            supervisor =sup.full_name
            update_msg =Message.objects.filter(student=student).filter(outgoing=True).filter(supervisor=sup)
            messages =Message.objects.filter(student=student).filter(supervisor=sup)
            print(supervisor)
        if check_coord:
            coord = Coordinator.objects.get(staff_no=adm)
            coordinator = coordinator.full_name
            update_msg = Message.objects.filter(student=student).filter(outgoing=True).filter(coordinator=coord)
            messages = Message.objects.filter(student=student).filter(coordinator=coord)
            print(coordinator)
            
        # messages = Message.objects.filter(student=student)
        # messages = JsonResponse(messages,safe=False)
        data = {}
        for msg in messages:
            time = msg.sent_on
            data[str(msg.id)] = {
                'student' : msg.student.full_name,
                'message_content' : msg.message_content,
                'time' : time.strftime("%b %d, %Y %H:%M"),
                'outgoing': msg.outgoing
            }
        data = json.dumps(data)
        return JsonResponse(data, safe=False)
        

class SendMessagesStudent(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/view-messages.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def post(self, request):
        msg = request.POST['message']
        print(request.POST['coordinator'])
        student = Student.objects.get(adm=request.user)
        check_sup = Supervisor.objects.filter(staff_no=request.POST['coordinator']).exists()
        check_coord = Coordinator.objects.filter(staff_no=request.POST['coordinator']).exists()
        if check_sup:
            supervisor = Supervisor.objects.get(staff_no=request.POST['coordinator'])
            new_msg = Message(student= student, supervisor=supervisor,message_content=msg,outgoing=False)
        if check_coord:
            coordinator = Coordinator.objects.get(staff_no=request.POST['coordinator'])
            new_msg = Message(student= student, coordinator=coordinator,message_content=msg,outgoing=False)
        new_msg.save()
        print(msg)
        
        
    # coordinator views
def unread_messages(user):
    coordinator = Coordinator.objects.get(staff_no=user)
    unread_msg = Message.objects.filter(coordinator=coordinator).filter(outgoing=False).filter(read_status=False).count()
    if unread_msg==0:
        unread_msg=''
    return unread_msg
        
        
class CoordinatorView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'coordinator/index.html'
    
    def test_func(self):
        user = self.request.user
        return Coordinator.objects.filter(staff_no=user).exists()

    def get(self, request):
        unread_msg = unread_messages(request.user)
        year = datetime.date.year
        current_year = AcademicYear.objects.get(active=True)
        allocated_supervisors = AllocatedSupervisor.objects.all().count()
        supervisors = Supervisor.objects.all().count()
        pending_applications = Application.objects.filter(status="P").count()
        seen_applications = Application.objects.exclude(status="P").count()
        context ={
            'year': current_year,
            'supervisors': supervisors,
            'allocated_supervisors': allocated_supervisors,
            'pending' : pending_applications,
            'seen': seen_applications,
            'unread_msg': unread_msg,
        }
        return render(request, self.template, context)
  
  
    # test_func for coordinator
def coordinator(request):
    user = request.user
    return Coordinator.objects.filter(staff_no=user).exists()


class SupervisorsCoordinator(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    form = forms.UpdateStatusForm
    template = 'coordinator/supervisors.html'

    def test_func(self):
        return coordinator(self.request)
        
    def get(self, request):
        user = request.user
        coordinator = Coordinator.objects.get(staff_no=user)
        supervisors = Supervisor.objects.filter(department=coordinator.department)
        print(supervisors)
        context = {
            'supervisors': supervisors
        }
        return render(request, self.template, context)
    
    
    
class CoordinatorApplications(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'coordinator/applications.html'
    form = forms.UpdateStatusForm
    
    def test_func(self):
        user = self.request.user
        return Coordinator.objects.filter(staff_no=user).exists()
        
    def get(self, request):
        user = self.request.user
        unread_msg = unread_messages(request.user)
        applications = Application.objects.all()
        context = {
            'form': self.form,
            'applications': applications,
            'unread_msg':unread_msg
        }
        return render(request, self.template, context)
    
    def post(self,request):
        form = self.form(request.POST or None)
        applications = Application.objects.all()
        if form.is_valid():
            print(request.POST)
            id=request.POST['id']
            a = Application.objects.get(pk=id)
            print(a)
            form = self.form(request.POST, instance=a)
            form.save()
            context ={
                'form': self.form,
                'applications':applications,
                'successfull': 'application status successfully updated'
            }
        else:
            context ={
                'form': self.form,
                'applications':applications,
                'failed' : 'failed to update status.check errors below \U0001F447'
            }
        return render(request,self.template,context )
    
class UpdateStatus(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    form = forms.UpdateStatusForm
    template = 'coordinator/update-status.html'

    def test_func(self):
        return coordinator(self.request)
        
    def get(self, request):
        unread_msg = unread_messages(request.user)
        applications = Application.objects.all()
        # status
        form = self.form,
        pending = Application.objects.filter(status='P')
        awaiting = Application.objects.filter(status='A')
        failed = Application.objects.filter(status='F')
        success = Application.objects.filter(status='S')
        for s in success:
            print(s.status)
        context = {
            'form' : form,
            'pending' : pending,
            'awaiting' : awaiting,
            'failed' : failed,
            'success' : success,
            'unread_msg':unread_msg
        }
        return render(request, self.template, context)
    
    def post(self,request):
        form = self.form(request.POST or None)
        
        if form.is_valid():
            print(request.POST)
            id=request.POST['id']
            a = Application.objects.get(pk=id)
            print(a)
            form = self.form(request.POST, instance=a)
            form.save()
            context1 ={
                'successfull': 'application status successfully updated'
            }
        else:
            context1={
                'failed' : 'failed to update status.check errors below \U0001F447'
            }
        pending = Application.objects.filter(status='P')
        awaiting = Application.objects.filter(status='A')
        failed = Application.objects.filter(status='F')
        success = Application.objects.filter(status='S')
        context = {
            'form' : form,
            'pending' : pending,
            'awaiting' : awaiting,
            'failed' : failed,
            'success' : success
        }
        # merge contexts 
        context.update(context1)
        return render(request,self.template,context )
        
# function to fetch list of students in a department  
def studentsInDepartment(user,src=None,user_type=None): 
    if user_type == 'supervisor':
       department = Supervisor.objects.get(staff_no=user) 
    else:
        department = Coordinator.objects.get(staff_no=user)
    courses = Course.objects.filter(department=department.department)
    # print(courses)
    students={}
    for course in courses:
        if src == 'allocated_list':
            students_per_class= Student.objects.filter(course_code=course).exclude(allocatedsupervisor__department=department.department)
        else:
            students_per_class= Student.objects.filter(course_code=course)

        for student in students_per_class:
            students[str(student.adm)] =  {
                'adm': student.adm,
                'name': student.full_name,
                'course':student.course_code.course_name,
                'year': student.admission_year,
            }
    # for key,student in students.items():
    #     print(student['adm'])
    #     print(student['name'])
    return students
        
class StudentList(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/student-list.html'
    # form = forms.StudentListForm
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        unread_msg = unread_messages(request.user)
        user = self.request.user
        # user=User.objects.get(username=user).values_list('username')
        students = studentsInDepartment(user,'student_list','coordinator')
            
        return render(request,self.template, {'students':students,'unread_msg':unread_msg})


class OrganizationCoordinator(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/organizations.html'
    # form = forms.StudentListForm
    
    def test_func(self):
        return coordinator(self.request) 
    
    def get(self, request):  
        organization_details ={}
        students = studentsInDepartment(request.user,'student_list','') 
        for key,student in students.items():
            std = Student.objects.get(adm=key)
            details = Organization.objects.filter(student__adm=key)
            for detail in details:
                organization_details[detail.student.adm] = {
                    'student': detail.student,
                    'organization': detail.organization,
                    'county': detail.county,
                    'town': detail.town,
                    'building': detail.building
                }
        print(organization_details)
        return render(request, self.template,{'organizations':organization_details})
         
         

class OrganizationCoordinatorPDF(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        organization_details ={}
        students = studentsInDepartment(request.user,'student_list','') 
        for key,student in students.items():
            std = Student.objects.get(adm=key)
            details = Organization.objects.filter(student__adm=key)
            for detail in details:
                organization_details[detail.student.adm] = {
                    'student': detail.student,
                    'organization': detail.organization,
                    'county': detail.county,
                    'town': detail.town,
                    'building': detail.building
                }
        context ={
            'organizations': organization_details,
            'date':datetime.date.today(),
        }
        pdf = render_to_pdf('coordinator/organization-pdf.html', context)
        return HttpResponse(pdf, content_type='application/pdf')
        
class NotificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    template = 'coordinator/notifications.html'
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        unread_msg = unread_messages(request.user)
        notification_list = Notification.objects.all().order_by('-date')
        paginator = Paginator(notification_list, 6) # Show 25 contacts per page
        page = request.GET.get('page')
        notifications = paginator.get_page(page)
        return render(request, self.template, {'notifications': notifications,'unread_msg':unread_msg})
    
    def post(self, request):
        form = self.form(request.POST or None)
        notifications = Notification.objects.all().order_by('-date')
       
            
class sendNotificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    template = 'coordinator/send-notification.html'
    form = forms.NotificationForm
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        return render(request, self.template,{ 'form': self.form})
    
    def post(self, request):
        notifications = Notification.objects.all().order_by('-date')
        cdn = Coordinator.objects.get(staff_no=request.user)
        form = self.form(request.POST or None)
        if form.is_valid():
            n = form.save(commit=False)
            n.department = cdn.department
            n.save()
            
            messages.success(request, 'Notification has been successfully sent')
        else:
            messages.warning(request,'Notification not sent, Please try again')
        
        return redirect('notifications')
    
    # view supervisors already allocated
class AllocatedSupervisorsView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    template = 'coordinator/allocated-supervisors.html'
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        unread_msg = unread_messages(request.user)
        # get coordinators department
        user = request.user
        department = Coordinator.objects.get(staff_no=user)
        supervisors = Supervisor.objects.filter(department=department.department)
        allocated_supervisors = AllocatedSupervisor.objects.filter(department=department.department)
        print(allocated_supervisors)
        context = {
            'supervisors': allocated_supervisors,
            'supervisors_list' : supervisors,
            'unread_msg':unread_msg
        }
        return render(request, self.template, context)
    
    def post(self,request):
        print (request.POST)
        student = request.POST['student']
        supervisor = request.POST['supervisor']
        department = Coordinator.objects.get(staff_no = request.user)
        department = Department.objects.get(dept_code=department.department.dept_code)
        # get instance of each
        student = Student.objects.get(adm=student)
        supervisor = Supervisor.objects.get(staff_no=supervisor)
        print(department,student,supervisor)
        instance = AllocatedSupervisor.objects.get(student=student)
        instance.supervisor=supervisor
        instance.save()
        message=student,'has been reassigned',supervisor
        print(request.method)
        
        messages.success(request, message)
        request.method = 'GET'
        print(request)
        return redirect('allocatedSupervisors')
    
class AllocateSupervisorView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/allocate-supervisor.html'
    # form = forms.StudentListForm
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        unread_msg = unread_messages(request.user)
        user = self.request.user
        # get coordinator's department
        department = Coordinator.objects.get(staff_no=user)
        # find students already allocated supervisors in a given department
        students_allocated = AllocatedSupervisor.objects.filter(department=department.department)        
        courses = Course.objects.filter(department=department.department)
        # get students in a given department who have not yet been allocated a lecturer
        students=studentsInDepartment(user,'allocated_list')
        
        supervisors = Supervisor.objects.filter(department=department.department)
        
        return render(request,self.template, {'students': students,'supervisors_list' : supervisors,'unread_msg':unread_msg})
    
    def post(self,request):
        print (request.POST)
        student = request.POST['student']
        supervisor = request.POST['supervisor']
        department = Coordinator.objects.get(staff_no = request.user)
        department = Department.objects.get(dept_code=department.department.dept_code)
        # get instance of each
        student = Student.objects.get(adm=student)
        supervisor = Supervisor.objects.get(staff_no=supervisor)
        print(department,student,supervisor)
        AllocatedSupervisor(student=student,supervisor=supervisor,department=department).save()
        
        messages.success(request, 'Allocation successfull')
        return redirect('allocatedSupervisors')
        
        
class MessagesCoordinator(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/messages.html'
    # form = forms.StudentListForm
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        unread_msg = unread_messages(request.user)
        coordinator = Coordinator.objects.get(staff_no=request.user)
        msg = Message.objects.filter(coordinator=coordinator).filter(read_status=False).order_by('-sent_on')
        # get list of student in department
        students = studentsInDepartment(request.user,'student_list')
        students = json.dumps(students)
        print(students)
        context = {
            'messages' : msg,
            'unread_msg':unread_msg,
            'students': students
        }
        return render(request, self.template, context)
        
class SendMessage(LoginRequiredMixin,UserPassesTestMixin,View):
    login_url = 'settings.LOGIN_URL'
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        return None
        
    def post(self, request):
        msg = request.POST['message']
        student = Student.objects.get(adm=request.POST['student'])
        coordinator = Coordinator.objects.get(staff_no=request.user)
        print(msg)
        new_msg = Message(student= student, coordinator=coordinator,message_content=msg,outgoing=True)
        new_msg.save()
    
class RefreshChatsCoordinator(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    
    def test_func(self):
        return coordinator(self.request)
    
    def post(self, request,adm):
        unread_msg = unread_messages(request.user)
        messages = Message.objects.filter(student=adm)
        # messages = JsonResponse(messages,safe=False)
        data = {}
        for msg in messages:
            time = msg.sent_on
            data[str(msg.id)] = {
                'student' : msg.student.full_name,
                'message_content' : msg.message_content,
                'time' : time.strftime("%b %d, %Y %H:%M"),
                'outgoing': msg.outgoing
            }
        data = json.dumps(data)
        return JsonResponse(data, safe=False)
    
    def get(self, request, adm):
        student = Student.objects.get(adm=adm)
        messages = Message.objects.filter(student=adm)
        update_msg = Message.objects.filter(student=adm).filter(outgoing=False)
        for msg in update_msg:
            print(msg)
            msg.read_status=True
            msg.save()
        unread_msg = unread_messages(request.user)
        # messages = JsonResponse(messages,safe=False)
        data = {}
        for msg in messages:
            time = msg.sent_on
            data[str(msg.id)] = {
                'student' : msg.student.full_name,
                'message_content' : msg.message_content,
                'time' : time.strftime("%b %d, %Y %H:%M"),
                'outgoing' : msg.outgoing
            }
        return render(request,'coordinator/message_per_person.html',{'messages': data,'student': student,'unread_msg':unread_msg})
        
        
        
class AssesmentReportCoordinator(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/assessment.html'
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        assessed = Assessment.objects.all()
        return render(request, self.template, {'assessed': assessed})
        

class AssesmentPDFCoordinator(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/assessment-pdf.html'
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        department = Coordinator.objects.get(staff_no=request.user)
        assessed = Assessment.objects.filter(department=department.department)
        pdf = render_to_pdf(self.template, {'assessed':assessed,'date':datetime.date.today()})
        return HttpResponse(pdf, content_type='application/pdf')# supervisor views

def supervisor(request):
    user = request.user
    return Supervisor.objects.filter(staff_no=user).exists()

def unread_messages_supervisor(user):
    supervisor = Supervisor.objects.get(staff_no=user)
    unread_msg = Message.objects.filter(supervisor=supervisor).filter(outgoing=False).filter(read_status=False).count()
    if unread_msg==0:
        unread_msg=''
    return unread_msg
class SupervisorView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    template = 'supervisor/students-assigned.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self,request):
        unread_msg = unread_messages_supervisor(request.user)
        supervisor = Supervisor.objects.get(staff_no=request.user)
        students = AllocatedSupervisor.objects.filter(supervisor=supervisor)
        
        # get organization detail for where each each student is at
        organization_details={}
        for student in students:
            # print(student.student.adm)
            adm =student.student.adm
            details = Organization.objects.filter(student=student.student)
            # print(details)
            for detail in details:
                organization_details[student.student.adm] = {
                    'adm': detail.student.adm,
                    'name' : detail.student.full_name,
                    'organization': detail.organization,
                    'county': detail.county,
                    'town': detail.town,
                    'building': detail.building
                }
        organization_details = json.dumps(organization_details)
        print(organization_details)
        context ={
            'students': students,
            'organization': organization_details,
            'unread_msg':unread_msg,
        }
        return render(request, self.template, context)
    
    
class Logbooks(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    template = 'supervisor/logbooks.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self,request):
        unread_msg = unread_messages_supervisor(request.user)
        supervisor = Supervisor.objects.get(staff_no=request.user)
        students = AllocatedSupervisor.objects.filter(supervisor=supervisor)
        
        logbook_details = {}
        
        for student in students:
            logbooks = Logbook.objects.filter(student=student.student)
            print(logbooks)
            for logbook in logbooks:
                logbook_details[logbook.student.adm] ={
                    'adm': logbook.student.adm,
                    'name':logbook.student.full_name,
                    'date':logbook.date,
                    'work_done': logbook.work_done,
                    
                }
        print(logbook_details)
        context ={
            'students':students,
            'logbook': logbook_details,
            'unread_msg':unread_msg,
        }
        return render(request, self.template, context)
    
    
class StudentLogbook(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    template = 'supervisor/student-logbook.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self,request, adm):
        unread_msg = unread_messages_supervisor(request.user)
        student = Student.objects.get(adm=adm)
        logbook = Logbook.objects.filter(student=student)
        print(logbook)
        
        return render(request, self.template, {'logbook':logbook, 'student': student,'unread_msg':unread_msg})
    

class LogbookPDF_supervisor(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'supervisor/logbook-pdf.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self, request, adm):
        student = Student.objects.get(adm=adm)
        logbook_details = Logbook.objects.filter(student=student)
        context ={
            'student' : student,
            'logbook' : logbook_details
        }
        pdf = render_to_pdf('supervisor/logbook-pdf.html', context)
        return HttpResponse(pdf, content_type='application/pdf')
    
    
class SendMessage_supervisor(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'supervisor/send-message.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self,request):
        supervisor = Supervisor.objects.get(staff_no=request.user)
        students = AllocatedSupervisor.objects.filter(supervisor=supervisor)
        
        context ={
            'students': students,
            'supervisor': supervisor
        }
        return render(request, self.template, context)
    
    
class MessagesSupervisor(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'supervisor/messages.html'
    # form = forms.StudentListForm
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self, request):
        unread_msg = unread_messages_supervisor(request.user)
        supervisor = Supervisor.objects.get(staff_no=request.user)
        msg = Message.objects.filter(supervisor=supervisor).filter(read_status=False).order_by('-sent_on')
        # get list of student in department
        students = students = AllocatedSupervisor.objects.filter(supervisor=supervisor)
        students_json ={}
        for std in students:
            students_json[str(std.student.adm)]={
                'adm':std.student.adm,
                'name':std.student.full_name,
            }
        students_json = json.dumps(students_json)
        print(students_json)
        context = {
            'messages' : msg,
            'unread_msg':unread_msg,
            'students': students_json,
        }
        return render(request, self.template, context)
    
    
class SendMessageSupervisor(LoginRequiredMixin,UserPassesTestMixin,View):
    login_url = 'settings.LOGIN_URL'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self, request):
        return None
        
    def post(self, request):
        msg = request.POST['message']
        student = Student.objects.get(adm=request.POST['student'])
        supervisor = Supervisor.objects.get(staff_no=request.user)
        print(msg)
        new_msg = Message(student= student, supervisor=supervisor,message_content=msg,outgoing=True)
        new_msg.save()
    
class RefreshChatsSupervisor(LoginRequiredMixin,UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    
    def test_func(self):
        return supervisor(self.request)
    
    def post(self, request,adm):
        unread_msg = unread_messages_supervisor(request.user)
        supervisor = Supervisor.objects.get(staff_no=request.user)
        messages = Message.objects.filter(student=adm).filter(supervisor=supervisor)
        # messages = JsonResponse(messages,safe=False)
        data = {}
        for msg in messages:
            time = msg.sent_on
            data[str(msg.id)] = {
                'student' : msg.student.full_name,
                'message_content' : msg.message_content,
                'time' : time.strftime("%b %d, %Y %H:%M"),
                'outgoing': msg.outgoing
            }
        data = json.dumps(data)
        return JsonResponse(data, safe=False)
    
    def get(self, request, adm):
        student = Student.objects.get(adm=adm)
        supervisor = Supervisor.objects.get(staff_no=request.user)
        messages = Message.objects.filter(student=adm).filter(supervisor=supervisor)
        update_msg = Message.objects.filter(student=adm).filter(outgoing=False)
        for msg in update_msg:
            print(msg)
            msg.read_status=True
            msg.save()
        unread_msg = unread_messages_supervisor(request.user)
        # messages = JsonResponse(messages,safe=False)
        data = {}
        for msg in messages:
            time = msg.sent_on
            data[str(msg.id)] = {
                'student' : msg.student.full_name,
                'message_content' : msg.message_content,
                'time' : time.strftime("%b %d, %Y %H:%M"),
                'outgoing' : msg.outgoing
            }
        return render(request,'supervisor/message_per_person.html',{'messages': data,'student': student,'unread_msg':unread_msg})
        
        
class AssesmentReportSupervisor(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'supervisor/assessment.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self, request):
        lecturer = Supervisor.objects.get(staff_no=request.user)
        assessed = Assessment.objects.filter(lecturer=lecturer)
        return render(request, self.template, {'assessed': assessed})
        

class AssesmentPDFSupervisor(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'supervisor/assessment-pdf.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self, request):
        department = Supervisor.objects.get(staff_no=request.user)
        assessed = Assessment.objects.filter(lecturer=department)
        pdf = render_to_pdf(self.template, {'assessed':assessed,'date':datetime.date.today()})
        return HttpResponse(pdf, content_type='application/pdf')


class AddAssessment(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'supervisor/new-assessment.html'
    
    def test_func(self):
        return supervisor(self.request)
    
    def get(self, request):
        students = studentsInDepartment(request.user,'student-list','supervisor')
        students = json.dumps(students)
        dept = Supervisor.objects.get(staff_no=request.user)
        dept = Department.objects.get(dept_code = dept.department.dept_code)
        print(dept)
        courses = Course.objects.filter(department=dept)
        
        return render(request, self.template, { 'students': students, 'courses':courses})
        
        
    def post(self, request):
        student =request.POST['student']
        student = Student.objects.get(adm=student)
        lecturer = Supervisor.objects.get(staff_no=request.user)
        department = Department.objects.get(dept_code=lecturer.department.dept_code)
        date = request.POST['date']
        print(student)
        check = Assessment.objects.filter(student=student).exists()
        if not check:
            instance = Assessment(student=student,lecturer=lecturer,department=department,date=date)
            instance.save()
            messages.success(request, 'Assessment has been successfully saved and sent to the coordinator')
        else:
            messages.error(request, 'Sorry! '+str(student)+' has already been assessed')
                           
        return redirect('addAssessment')