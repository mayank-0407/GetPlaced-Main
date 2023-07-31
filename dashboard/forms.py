from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from home.models import CompanyProfile, StudentProfile
from .models import CompanyAnnouncement,Blog

class StudentPhotoForm(ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "image"
        ]
        
class CompanyPhotoForm(ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            "image"
        ]

class StudentCVForm(ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "cv"
        ]
        
class CompanyAnnouncementForm(ModelForm):
    class Meta:
        model = CompanyAnnouncement
        fields = [
            "internship_round",
            "round_name",
            "prev_round_for_result",
            "message",
            "file",
            "file_for_prev_result",
        ]

class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = [
            "title",
            "short_description",
            "brief_description",
            "image",
        ]

class NewUserForm(ModelForm):
    class Meta:
        model = CompanyAnnouncement
        fields = [
            "file",
        ]