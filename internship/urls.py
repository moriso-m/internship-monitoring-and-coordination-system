from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path("register/", views.Register.as_view(), name="register"),
    
    # student routes
    path('student/', views.StudentView.as_view(), name='studentIndex'),
    path('student/application', views.Apply.as_view(), name='application'),
    path('student/application-status', views.ApplicationStatus.as_view(), name='applicationStatus'),
    path('student/logbook', views.FillLogbook.as_view(), name='logbook'),
    path('student/view-logbook', views.ViewLogbook.as_view(), name='viewLogbook'),
    path('student/logbook-pdf', views.LogbookPDF.as_view(), name='logbookPdf'),
    path('student/logbook-guidelines', views.LogbookGuidelines.as_view(), name='logbookGuidelines'),
    path('student/final-report', views.FinalReportGuidelines.as_view(), name='finalReport'),
    path('student/organization', views.OrganizationView.as_view(), name='organization'),
    
    # coordinator routes
    path("coordinator/", views.CoordinatorView.as_view(), name="coordinatorIndex"),
    path("coordinator/applications", views.CoordinatorApplications.as_view(), name="coordinatorApplications"),
    path("coordinator/update-status", views.UpdateStatus.as_view(), name="updateStatus"),
    path("coordinator/student", views.StudentList.as_view(), name="students"),
    path("coordinator/notifications", views.NotificationView.as_view(), name="notifications"),
    path("coordinator/send-notification", views.sendNotificationView.as_view(), name="sendNotification"),
    path("coordinator/allocated-supervisors", views.AllocatedSupervisorsView.as_view(), name="allocatedSupervisors"),
    path("coordinator/allocate-supervisor", views.AllocateSupervisorView.as_view(), name="allocateSupervisor"),
  
]