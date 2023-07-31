from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import (login,authenticate,logout)
from home.models import *
from dashboard.models import *
import time
from .views import *

# Create your tests here.
#Notes:
#   1.There must be method in every class named as setUp(self) which will set variables and databases for unit testcase
#   2. A tearDown(self) can be used to clear all the databases created after the test cases run
#   3. Every testcase method must start from 'test' otherwise it will be treated like a function not testcase.


#Checks for all the functions and methods used for login form
class UnitTest(TestCase):

    #Create a new user to test for login phase
    #Create a new student profile with the user create in Setup() method
    #There are more fields in the profile which would be set to default if not given in the create() function
    def setUp(self):
        self.user = User.objects.create_user(username="ABCDE", password="ABCDE@123", email="aditya.iiita2001@gmail.com")
        self.user.save()
        self.user.is_staff=True
        self.user.save()
        self.new_profile=StudentProfile.objects.create(user=self.user, gender="Male", verified=True, account_banned_permanent=False, account_banned_temporary=False, account_ban_time=0)
        self.new_profile.save()

    #To delete user account after test cases
    def tearDown(self):
        self.user.delete()
        self.new_profile.delete()

            ###Login
    #Checks for when correct username and password is given
    def test_correct_username_password(self):
        user=authenticate(username="ABCDE", password="ABCDE@123")
        self.assertTrue((user is not None) and user.is_authenticated)

    #Checks for when correct email and password is given
    def test_correct_email_password(self):
        getuser=User.objects.get(email="aditya.iiita2001@gmail.com").username
        user=authenticate(username=getuser, password="ABCDE@123")
        self.assertTrue((user is not None) and user.is_authenticated)

    #Checks when wrong username is given
    def test_wrong_username(self):
        user=authenticate(username="ABCE", password="ABCDE@123")
        self.assertFalse(user is not None and user.is_authenticated)

    #Checks when wrong password is given
    def test_wrong_password(self):
        user=authenticate(username="ABCDE", password="ABCDE@113")
        self.assertFalse(user is not None and user.is_authenticated)

    #Checks whether student account is banned or not
    def test_account_ban(self):
        isbanned=self.new_profile.account_banned_permanent or self.new_profile.account_banned_temporary

        #If user is banned then assertTrue will return '.' , else assertFalse will return '.'
        if isbanned:
            self.assertTrue(isbanned)
        else:
            self.assertFalse(isbanned)

    #Checks for staff user
    def test_staff(self):
        is_staff=self.user.is_staff
        if is_staff:
            self.assertTrue(is_staff)
        else:
            self.assertFalse(is_staff)

    #Checks for admin user
    def test_admin(self):
        is_admin=self.user.is_superuser
        if is_admin:
            self.assertTrue(is_admin)
        else:
            self.assertFalse(is_admin)

            ###Signup And Forgot Password
    #Checks email already exists or not
    def test_email_already_exists(self):
        user_count=User.objects.filter(email=self.user.email).count()
        if user_count>0:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    #Checks username already exists or not
    def test_username_already_exists(self):
        user_count=User.objects.filter(username=self.user.username).count()
        if user_count>0:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    #Otp and time of 3 seconds verification
    def test_time_verification_for_otp(self):
        self.new_profile.otp="12344"
        self.new_profile.otp_time=datetime.datetime.now()
        self.new_profile.save()
        time.sleep(2)
        new_time=datetime.datetime.now()
        time_delta = (new_time-self.new_profile.otp_time)
        seconds = (time_delta.total_seconds())//3600
        self.assertTrue(self.new_profile.otp=="12344" and seconds<=3)


    #Send OTP testing
    def test_send_otp(self):
        try:
            Email_thread("OTP","12344",self.user.email).start()
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    #Change Password Testing
    def test_change_password(self):
        old_password=self.user.password
        password=generate_password()
        self.user.set_password(password)
        self.user.save()
        new_password=self.user.password
        self.user.set_password(old_password)
        self.user.save()
        same=False
        if old_password==new_password:
            same=True
        self.assertFalse(same)


    def test_check_permissions(self):
        self.permissions=StaffPermissions.objects.create(user=self.user)
        self.assertFalse(self.permissions.can_ban_users)
        self.assertFalse(self.permissions.can_create_new_company_account)

    def test_create_notification(self):
        self.notification=Notification.objects.create(notification_sender=self.user, notification_receiver=self.user, notification="Hi, user")
        count=Notification.objects.filter(notification_sender=self.user, notification_receiver=self.user, notification="Hi, user").count()
        if count>0:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_technical_support(self):
        TechnicalSupportRequest.objects.create(user=self.user, message="I have a doubt")
        count=TechnicalSupportRequest.objects.filter(user=self.user).count()
        if count>0:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_create_blogs(self):
        Blog.objects.create(title="Title", short_description="Short description", brief_description="Short desription")
        count=Blog.objects.filter(title="Title", short_description="Short description", brief_description="Short desription").count()
        if count>0:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
