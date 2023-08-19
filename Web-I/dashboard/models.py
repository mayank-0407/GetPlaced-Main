from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class StaffPermissions(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    can_access_student_inactive_accounts=models.BooleanField(default=False)
    can_access_company_inactive_accounts=models.BooleanField(default=False)
    can_ban_users=models.BooleanField(default=False)
    
    can_manage_blogs=models.BooleanField(default=False)
    can_manage_technical_support=models.BooleanField(default=False)
    can_give_notifications=models.BooleanField(default=False)
    
    #For admins only
    can_unban_users=models.BooleanField(default=False)
    can_manage_staff_accounts=models.BooleanField(default=False)
    can_delete_staff_accounts=models.BooleanField(default=False)
    
    can_manage_sessions=models.BooleanField(default=False)
    create_new_accounts=models.BooleanField(default=False)
    manage_CGPA=models.BooleanField(default=False)
    remove_students=models.BooleanField(default=False)
    remove_companies=models.BooleanField(default=False)

    can_manage_internships=models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class Session(models.Model):
    name=models.TextField()
    active=models.BooleanField(default=True)
    created_on=models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.name

class Internship(models.Model):
    session=models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    company=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    internship_name=models.TextField()
    stipend=models.FloatField(default=0, null=True)
    internship_duration=models.IntegerField(default=0, null=True)
    internship_position=models.TextField()
    minimum_cgpa=models.FloatField(default=5.0, null=True)
    prerequisite=models.TextField()
    result_announced=models.BooleanField(default=False)

    def __str__(self):
        if self.company:
            return self.company.username + str(" -> ") + self.internship_name
        else:
            return 'NILL'
        
class InternshipFinalResult(models.Model):
    internship=models.ForeignKey(Internship, on_delete=models.CASCADE, null=True, blank=True)
    company=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='company')
    student=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student')
    
    def __str__(self):
        if self.internship:
            if self.student:
                return str(self.student) + " is an intern in " + str(self.internship)
            else:
                return str(self.internship)
        else:
            if self.student:
                return str(self.student)
            else:
                return "NIL"

class CompanyAnnouncement(models.Model):
    internship=models.ForeignKey(Internship, on_delete=models.CASCADE, null=True, blank=True)
    company=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    general_announcement=models.BooleanField(default=False)
    internship_round=models.TextField()
    round_name=models.TextField()
    first_round=models.BooleanField(default=False)
    last_round=models.BooleanField(default=False)
    last_round_result_announced=models.BooleanField(default=False)
    prev_round_for_result=models.TextField()
    last_date_to_apply=models.DateTimeField(default=datetime.datetime.now())
    announcement_date=models.DateTimeField(default=datetime.datetime.now())
    message=models.TextField()
    file=models.FileField(upload_to='post_files/', null=True, blank=True)
    file_for_prev_result=models.FileField(upload_to='post_files/', null=True, blank=True)

    def __str__(self):
        if self.company:
            return str(self.company.username) + " Round " + str(self.internship_round)
        else:
            return 'NILL'


class ProfileVisibility(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    to_registered_companies=models.BooleanField(default=False)
    to_all_companies=models.BooleanField(default=False)
    to_all_students=models.BooleanField(default=False)
    to_all=models.BooleanField(default=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return 'NILL'

class StudentRegistration(models.Model):
    company=models.ForeignKey(CompanyAnnouncement, on_delete=models.CASCADE, null=True, blank=True)
    student=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_of_registrations=models.DateTimeField(default=datetime.datetime.now())
    result_status=models.IntegerField(default=0)
    internship_cleared=models.BooleanField(default=False)
    #Status 0 : Not Announced
    #Status 1: Cleared
    #Status 2: Rejected
    #Status 3: Placed in another internship

    def __str__(self):
        return str(self.student.username) + " registered in " + str(self.company)

class ProfilePermissions(models.Model):
    user_who_can_see=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='can_see')
    user_whose_to_see=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='whose_to_see')


    def __str__(self):
        if self.user_who_can_see:
            if self.user_whose_to_see:
                return str(self.user_who_can_see) + " can see " + str(self.user_whose_to_see) + " profile"
            else:
                return str(self.user_who_can_see)
        else:
            if self.user_whose_to_see:
                return str(self.user_whose_to_see)
            else:
                return "NIL"

class Blog(models.Model):
    title=models.TextField()
    short_description=models.TextField()
    brief_description=models.TextField()
    image=models.ImageField(upload_to='post_images/', null=True, blank=True)
    date_of_announcement=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
class TechnicalSupportRequest(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    continued_support=models.BooleanField(default=False)
    main_support_id=models.IntegerField(default=0)
    message=models.TextField()
    date=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user)

class Notification(models.Model):
    notification_sender=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_sender')
    notification_receiver=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_receiver')
    notification=models.TextField()
    date=models.DateTimeField(default=datetime.datetime.now())
    
    def __str__(self):
        return str(self.notification_sender) + '->' + str(self.notification_receiver)

class ChatRequest(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="customer")
    message=models.TextField()
    message_time=models.DateTimeField(default=datetime.datetime.now())
    chat_ended=models.BooleanField(default=False)
    engaged=models.BooleanField(default=False)
    engaged_user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="staff")
    
class ChatResponse(models.Model):
    chat_request=models.ForeignKey(ChatRequest, on_delete=models.CASCADE, null=True)
    responder=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    username=models.TextField()
    message=models.TextField()
    message_time=models.DateTimeField(default=datetime.datetime.now())
    mess_time_str=models.TextField()
    read=models.BooleanField(default=False)
    read_s=models.BooleanField(default=False)

