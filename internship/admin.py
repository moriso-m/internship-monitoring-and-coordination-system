from django.contrib import admin
from .models import Department, Course, Student, Coordinator,Supervisor,Application, Organization, Message, Logbook, AcademicYear

# register models
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Coordinator)
admin.site.register(Supervisor)
admin.site.register(Application)
admin.site.register(Organization)
admin.site.register(Message)
admin.site.register(Logbook)
admin.site.register(AcademicYear)