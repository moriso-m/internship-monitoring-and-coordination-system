from django import forms
from .models import Student, Department, Application, Logbook, Message
from django.contrib.auth.models import User


# my form models

class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Admission no/ Staff no', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-3','placeholder':'Adm no/ staff no'}
                                ))
    password = forms.CharField(label= 'Password:', max_length=50, required=True,
                               widget = forms.PasswordInput(
                                   attrs = {'class':'form-control col-lg-3', 'placeholder': 'Password...'}
                               ))
    class Meta:
        model = User
        fields = ['username', 'password']

class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Admission no/ Staff no', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-3','placeholder':'Adm no/ staff no'}
                                ))
    email = forms.EmailField(label= 'Email address:', max_length=50, required=True,
                               widget = forms.TextInput(
                                   attrs = {'class':'form-control col-lg-3', 'placeholder': 'Email address...'}
                               ))
    password = forms.CharField(label= 'Password:', max_length=50, required=True,
                               widget = forms.PasswordInput(
                                   attrs = {'class':'form-control col-lg-3', 'placeholder': 'Password...'}
                               ))
    confirm_password = forms.CharField(label= 'Confirm Password:', max_length=50, required=True,
                               widget = forms.PasswordInput(
                                   attrs = {'class':'form-control col-lg-3', 'placeholder': ' confirm Password...'}
                               ))
    
    class Meta:
        model = User
        fields =['username','email', 'password']

class ApplicationForm(forms.ModelForm):
    organization = forms.CharField(label='Organization', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-4',
                                           'placeholder':'Organization ...'}
                                ))
    location = forms.CharField(label='Location', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-4 ',
                                           'placeholder':'Location ...'}
                                ))
    PO_Box = forms.CharField(label='P.O BOX', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-4 ',
                                           'placeholder':'p.o box ...'}
                                ))
    branch = forms.CharField(label='Organization`s Branch', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-4 ',
                                           'placeholder':'branch ...'}
                                ))
    
    class Meta:
        model = Application
        fields = '__all__'
        exclude = ['id', 'student', 'status']
