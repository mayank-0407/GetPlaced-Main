from django.contrib import admin
from .models import StudentProfile, CompanyProfile, Query
# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(CompanyProfile)
admin.site.register(Query)