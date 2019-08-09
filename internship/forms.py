from django import forms
from .models import Student, Department,  Logbook, Message, Organization, Application, Notification,AllocatedSupervisor
from django.contrib.auth.models import User


# my form models

class LoginForm(forms.ModelForm):
    username = forms.CharField(label='Admission no/ Staff no', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-md-8 offset-md-2','placeholder':'Adm no/ staff no'}
                                ))
    password = forms.CharField(label= 'Password:', max_length=50, required=True,
                               widget = forms.PasswordInput(
                                   attrs = {'class':'form-control col-md-8 offset-md-2', 'placeholder': 'Password...'}
                               ))
    class Meta:
        model = User
        fields = ['username', 'password']

class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Admission no/ Staff no', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-md-8 offset-md-2','placeholder':'Adm no/ staff no'}
                                ))
    email = forms.EmailField(label= 'Email address:', max_length=50, required=True,
                               widget = forms.TextInput(
                                   attrs = {'class':'form-control col-md-8 offset-md-2', 'placeholder': 'Email address...'}
                               ))
    password = forms.CharField(label= 'Password:', max_length=50, required=True,
                               widget = forms.PasswordInput(
                                   attrs = {'class':'form-control col-md-8 offset-md-2', 'placeholder': 'Password...'}
                               ))
    confirm_password = forms.CharField(label= 'Confirm Password:', max_length=50, required=True,
                               widget = forms.PasswordInput(
                                   attrs = {'class':'form-control col-md-8 offset-md-2', 'placeholder': ' confirm Password...'}
                               ))
    
    class Meta:
        model = User
        fields =['username','email', 'password']
    
    def validate_password(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['confirm_password']
        if password1 != password2:
            raise forms.ValidationError('The two passwords do not match')
        

class ApplicationForm(forms.ModelForm):
    organization = forms.CharField(label='Organization:', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-md-8 offset-md-2',
                                           'placeholder':'Organization ...'}
                                ))
    PO_BOX = forms.CharField(label='P.O BOX:', max_length=50, required=False ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-md-8 offset-md-2',
                                           'placeholder':'p.o box ...'}
                                ))
    branch = forms.CharField(label='Organization`s Branch / Location:', max_length=50, required=True ,
                                widget= forms.TextInput(
                                    attrs={'class':'form-control col-lg-8 offset-md-2',
                                           'placeholder':'branch ...'}
                                ))
    
    class Meta:
        model = Application
        fields = '__all__'
        exclude = ['id', 'student', 'status']


class UpdateStatusForm(forms.ModelForm):
    status =forms.ChoiceField(choices =(
        ('','......'),
        ( 'P', 'Pending'),
        ( 'A', 'Awaiting'),
        ('F', 'Failed'),
        ('S', 'Successfull'),
        ),
        widget=forms.Select(attrs={'class': 'form-control'}),required=True)
    
    class Meta:
        model = Application
        fields = ['status']

class LogbookForm(forms.ModelForm):
    work_done = forms.CharField(label='Work done today:', required=True ,
                                widget= forms.Textarea(
                                    attrs={'class':'form-control col-lg-12',
                                           'id': 'work',
                                           'placeholder':'Tasks done ...',
                                           'rows' : '5',
                                           'columns' : '10'
                                        }
                                ))
    # date = forms.DateField(widget= forms.DateInput(
    #                             attrs={'class':'form-control col-lg-4 ',
    #                                     'placeholder':'Date ...'
    #                                 }
    #                         ))
    week = forms.CharField(label="Week:",widget= forms.TextInput(
                            attrs={'class':'form-control col-md-6 offset-md-3',
                                    'placeholder':'Week in digit format'
                                }
                        ))
    class Meta:
        model = Logbook
        exclude = ['student','date']


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = '__all__'


class NotificationForm(forms.ModelForm):
    content = forms.CharField(label='Notification', required=True ,
                            widget= forms.Textarea(
                                attrs={'class':'form-control',
                                        'placeholder':'Notification content ... \U0001F514',
                                        'rows' : '5',
                                        'columns' : '6'
                                    }
                            ))
    
    class Meta:
        model = Notification
        fields =["content"]


class AllocateSupervisorForm(forms.ModelForm):
    
    class Meta:
        model = AllocatedSupervisor
        fields = '__all__'
