from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from .models import Student, Coordinator, Course, Department, Application
from . import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
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
                pass
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
    
    
class ApplicationStatus(LoginRequiredMixin, UserPassesTestMixin, View):
    template = 'student/application-status.html'
    
    def test_func(self):
        user = self.request.user
        return Student.objects.filter(adm=user).exists()
        
    def get(self, request):
        applications = Application.objects.all()
        return render(request, self.template, {'applications' : applications })
        
        
    # coordinator views
class CoordinatorView(LoginRequiredMixin, UserPassesTestMixin, View):
    template = 'coordinator.html'
    
    def get(self, request):
        return render(request, self.template)