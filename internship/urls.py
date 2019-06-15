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
    
    # coordinator routes
    path("coordinator/", views.CoordinatorView.as_view(), name="coordinatorIndex")
  
]