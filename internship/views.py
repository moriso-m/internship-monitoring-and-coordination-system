from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .models import Student, Coordinator, Course, Department, Application, Logbook, AcademicYear, AllocatedSupervisor
from . import forms
# import utils for creating pdf
from .utils import render_to_pdf
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
import datetime
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
                return redirect('studentIndex')
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
            # redirect to appropriate portal
            if student:
                return redirect('studentIndex')
            elif coordinator:
                return redirect('coordinatorIndex')
            else:
                return redirect('admin')
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
            
            if student or coordinator:
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
                
                context ={
                    'form' : forms.LoginForm,
                    'account_created' : 'Account has been successfully created'
                }
                return render(request, 'login.html', context)
            
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
        return render(request, self.template, { 'form':self.form})
    
    def post(self, request):
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
                    'success' :  'Your application has been successfully sent'
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
        user = self.request.user
        student =Student.objects.get(adm=user)
        applications = Application.objects.filter(student= student)
        return render(request, self.template, {'applications' : applications })
        
    
# fill logbook view
class FillLogbook(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/fill-logbook.html'
    form = forms.LogbookForm
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        return render(request, self.template, { 'form':self.form})
    
    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            student = Student.objects.get(adm=request.user)
            instance = form.save(commit=False)
            instance.student = student
            instance.save()
            context ={
                    'form' : self.form(None),
                    'success' :  'details successfully filled in your logbook'
            }
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
        user= self.request.user
        student = Student.objects.get(adm = user)
        logbook_details = Logbook.objects.filter(student=student)
        print(logbook_details)
        context ={
            'logbook' : logbook_details
        }
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
        return render(request, self.template)
    
    
class OrganizationView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'student/organization.html'
    form = forms.OrganizationForm
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
    
    def get(self, request):
        return render(request, self.template, {'form': self.form})
    
    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            student = Student.objects.get(adm=request.user)
            
            instance = form.save(commit=False)
            instance.student = student
            instance.save()
            context ={
                    'form' : form,
                    'success' :  'details successfully filled in your logbook'
            }           
        else:
            context = {
                'form': self.form(request.POST),
            } 
        
        return render(request, self.template, context)
    # coordinator views
class CoordinatorView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    template = 'coordinator/index.html'
    
    def test_func(self):
        user = self.request.user
        return Coordinator.objects.filter(staff_no=user).exists()

    def get(self, request):
        year = datetime.date.year
        current_year = AcademicYear.objects.get(active=True)
        allocated_supervisors = AllocatedSupervisor.objects.all()
        pending_applications = Application.objects.filter(status="P").count()
        seen_applications = Application.objects.exclude(status="P").count()
        context ={
            'year': current_year,
            'supervisors': allocated_supervisors,
            'pending' : pending_applications,
            'seen': seen_applications,
        }
        return render(request, self.template, context)
  
  
    # test_func for coordinator
def coordinator(request):
    user = request.user
    return Coordinator.objects.filter(staff_no=user).exists()


class CoordinatorApplications(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    redirect_field_name = 'redirect_to'
    
    
    template = 'coordinator/applications.html'
    
    def test_func(self):
        user = self.request.user
        return Coordinator.objects.filter(staff_no=user).exists()
        
    def get(self, request):
        user = self.request.user
        applications = Application.objects.all()
        return render(request, self.template, {'applications' : applications })
    
    
class UpdateStatus(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = settings.LOGIN_URL
    
    form = forms.UpdateStatusForm
    template = 'coordinator/update-status.html'

    def test_func(self):
        return coordinator(self.request)
        
    def get(self, request):
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
            'success' : success
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
        
        
class StudentList(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = 'settings.LOGIN_URL'
    template = 'coordinator/student-list.html'
    # form = forms.StudentListForm
    
    def test_func(self):
        return coordinator(self.request)
    
    def get(self, request):
        students = Student.objects.filter(course_code='COM' or 'BIT')
        print(students)
        return render(request,self.template, {'students': students})

