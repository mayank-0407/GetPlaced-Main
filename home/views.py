from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,datetime,array,secrets
from twilio.rest import Client
from .forms import UserForm
from .models import StudentProfile, CompanyProfile, Query
from dashboard.models import CompanyAnnouncement, ProfilePermissions, Blog, ProfileVisibility
from dashboard.views import dashboard
import math,random,string,array,secrets
from os import urandom
from random import choice
import os
from django.http import FileResponse
from threading import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders
from functools import lru_cache
from django.http import JsonResponse
from django.core import serializers


# def email(request):
#     message =f'Your account has been banned temporarily for days.<br> Account is banned by, contact this email for any query.'
#     user_name=f'fdsfsf'
#     return render(request,'home/email.html',{'user_name': user_name, 'message':message})

class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)

def secureImage(request, file):
    try:
        document=Blog.objects.get(image="post_images/"+file)
        # return HttpResponse("ERROR")
        return FileResponse(document.image)
    except:
        pass
    if request.user.is_authenticated==True:
        try:
            document=StudentProfile.objects.get(image="post_images/"+file)
            if document.user==request.user:
                return FileResponse(document.image)
            else:
                if check_student_permissions(document.user)==True or check_profile_permissions(request, document.user)==True:
                    return FileResponse(document.image)
                else:
                    return redirect('home')
        except:
            try:
                document=CompanyProfile.objects.get(image="post_images/"+file)
                if document.user==request.user:
                    return FileResponse(document.image)
                else:
                    if check_company_permissions(document.user)==True or check_profile_permissions(request, document.user)==True:
                        return FileResponse(document.image)
                    else:
                        return redirect('home')
            except:
                return redirect('home')
    else:
        return redirect('home')

def secureFile(request, file):
    if request.user.is_authenticated==False:
        return error(request,"You are currently logged out")
    try:
        document=StudentProfile.objects.get(cv="post_files/"+file)
        if document.user==request.user or request.user.is_staff:
            return FileResponse(document.cv)
        else:
            if check_student_permissions(document.user)==True or check_profile_permissions(request, document.user)==True:
                return FileResponse(document.cv)
            else:
                return error(request,"You have not permissions to view this link")
    except:
        try:
            document=CompanyAnnouncement.objects.get(file="post_files/"+file)
            return FileResponse(document.file)
            # if document.company==request.user or request.user.is_staff:
            #     return FileResponse(document.file)
            # else:
            #     if check_profile_permissions(request, document.user)==True:
            #         return FileResponse(document.file)
            #     else:
            #         return redirect('home')
        except:
            try:
                document=CompanyAnnouncement.objects.get(file_for_prev_result="post_files/"+file)
                return FileResponse(document.file_for_prev_result)
                # if document.company==request.user or request.user.is_staff:
                #     return FileResponse(document.file_for_prev_result)
                # else:
                #     if check_company_permissions(document.user)==True or check_profile_permissions(request, document.user)==True:
                #         return FileResponse(document.file_for_prev_result)
                #     else:
                #         return redirect('home')
            except:
                try:
                    document=Blog.objects.get(file="post_files/"+file)
                    return FileResponse(document.file)
                except:
                    return error(request,"You have not permissions to view this link")

def check_profile_permissions(request, user):
    if request.user == user:
        return True
    try:
        ProfilePermissions.objects.get(user_who_can_see=request.user,user_whose_to_see=user)
        return True
    except:
        pass
    try:
        my_permissions=ProfileVisibility.objects.get(user=user)
        if my_permissions.to_all==True:
            return True
        if my_permissions.to_all_students==True:
            if request.user.last_name!=settings.COMPANY_MESSAGE:
                return True
        if my_permissions.to_all_companies==True:
            if request.user.last_name==settings.COMPANY_MESSAGE:
                return True
        return False
    except:
        return False


def check_student_permissions(user):
    return False

def check_company_permissions(user):
    return False

def home(request):
    data=get_my_profile(request)
    blogs=Blog.objects.all().order_by('-date_of_announcement')
    return render(request, 'home/homepage.html', context={"data": data, "blogs": blogs})

def home_(request,info):
    data=get_my_profile(request)
    blogs=Blog.objects.all().order_by('-date_of_announcement')
    return render(request, 'home/homepage.html', context={"data": data, "blogs": blogs, "info": info})

def get_my_profile(request):
    data={}
    try:
        data=StudentProfile.objects.get(user=request.user)
    except:
        try:
            data=CompanyProfile.objects.get(user=request.user)
        except:
            data={}
    return data

def SEND_OTP_TO_PHONE(mobile_number, country_code, message):
    client = Client(settings.PHONE_ACCOUNT_SID_TWILIO, settings.PHONE_ACCOUNT_AUTH_TOKEN_TWILIO)
    message = client.messages.create(
                        body=str(message),
                        from_= settings.PHONE_NUMBER_TWILIO,
                        to=str(country_code)+str(mobile_number)
                    )

def SENDMAIL(subject, message, email):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    checker = User.objects.get(email=email)
    username = checker.username
    html_content = render_to_string("home/email.html",{'message': message, 'user_name': username})
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject,text_content,email_from,recipient_list)
    email.mixed_subtype = 'related'
    email.attach_alternative(html_content,"text/html")
    email.send()
    # return render(request,'home/email.html',{'title':'send an email'})
    # send_mail( subject, message, email_from, recipient_list )

def signup(request):
    if request.method=="POST":
        signup_type=request.POST.get('signup_type')
        email=request.POST.get('email')
        username=request.POST.get('username')
        if email_in_use(email):
            user=User.objects.get(email=email)
            if user.is_active==True:
                return JsonResponse({"error": "This email is already registered"}, status=400)
            user.delete()
        if username_in_use(username):
            user=User.objects.get(username=username)
            if user.is_active==True:
                return JsonResponse({"error": "Username is already in use"}, status=400)
            user.delete()
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            user=User.objects.get(email=email)
            user.is_active=False
            user.email=email
            user.save()
        else:
            return JsonResponse({"error": str(form.errors)}, status=400)
        if int(signup_type)==1:
            profile=StudentProfile.objects.create(user=user)
        else:
            profile=CompanyProfile.objects.create(user=user, original_user=user)
        message = f'New signup request has been detected from your email. Click the given URL to confirm the signup '
        if signup_send_notification(email,profile,message)==False:
            return JsonResponse({"error": "Error in sending notification."},status=400)
        return JsonResponse({"success": "Signup Successful"}, status=200)
    else:
        return render(request, 'home/signup_page.html', context={})

def generate_code(length):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code = ""
    for i in range(length) :
        code += digits[math.floor(random.random() * 62)]
    return code

def signup_send_notification(email, p, message):
    try:
        code=p.user.username + generate_code(50)
        url=settings.BASE_URL+'/signup/verify/'+code
        subject = 'Signup Request detected in Clean Frame'
        message+=url + ' , and it expires in 15 minutes.'
        Email_thread(subject,message,email).start()
        p.unique_code=str(code)
        p.unique_code_time=datetime.datetime.now()
        p.save()
        return True
    except:
        return False

def signup_verification(request, code):
    try:
        profile=StudentProfile.objects.get(unique_code=code)
    except:
        try:
            profile=CompanyProfile.objects.get(unique_code=code)
        except:
            # To confuse hacker
           return render(request, 'home/signup_page.html', context={"code_message": "Account submitted for verification Successfully"})
    if profile.user.is_active:
        return render(request, 'home/signup_page.html', context={"code_message": "Account submitted for verification Successfully"})
    prev_time=profile.unique_code_time
    profile.unique_code_time=datetime.datetime.now()
    profile.save()
    try:
        profile=StudentProfile.objects.get(unique_code=code)
    except:
        profile=CompanyProfile.objects.get(unique_code=code)
    new_time=profile.unique_code_time
    time_delta = (new_time-prev_time)
    minutes = (time_delta.total_seconds())/60
    if minutes<settings.OTP_EXPIRE_TIME:
        user=profile.user
        user.is_active=True
        user.save()
        subject = 'Successful Signup in Clean Frame'
        message = f'Your account has been submitted for verification to our backend staff.'
        Email_thread(subject,message,profile.user.email).start()
        return render(request, 'home/signup_page.html', context={"code_message": "Account submitted for verification Successfully"})
    else:
        message = f'Previous Link expired. Click the new URL to confirm the signup '
        if signup_send_notification(profile.user.email,profile,message)==False:
            return JsonResponse({"error": "Error in sending notification."},status=400)
        return render(request, 'home/signup_page.html', context={"code_message": "This link is expired, we have send a new link, check it."})

def generate_otp():
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""
    for i in range(7) :
        OTP += digits[math.floor(random.random() * 62)]
    return OTP

def email_in_use(email):
    try:
        user=User.objects.get(email=email)
        return True
    except:
        return False

def username_in_use(username):
    try:
        user=User.objects.get(username=username)
        return True
    except:
        return False

def take_me_to_backend(request):
#to be modified
    return redirect('dashboard')


def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')

def login_request(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method=='POST':
        useremail=request.POST.get('user_email')
        password=request.POST.get('password')
        try:
            checker = User.objects.get(username=useremail)
            user = authenticate(request, username=useremail, password=password)
            if user is not None:
                pass
            else:
                return JsonResponse({"error": "Invalid Credentials"}, status=400)
        except:
            try:
                checker = User.objects.get(email=useremail)
                user = authenticate(request, username=checker.username, password=password)
                if user is not None:
                    pass
                else:
                    return JsonResponse({"error": "Invalid Credentials"}, status=400)
            except:
                return JsonResponse({"error": "Invalid Credentials"}, status=400)
        if user.is_active==False:
            return JsonResponse({"error": "Email Address has not been verified."}, status=400)
        if user.is_superuser or user.is_staff:
            login(request,user)
            return JsonResponse({"success": "Login is Successful."}, status=200)            
        if user.last_name==settings.COMPANY_MESSAGE:
            try:
                s=CompanyProfile.objects.get(user=user)
            except:
                return JsonResponse({"error": "Profile not found, signup again!!"}, status=400)
        else:
            try:
                s=StudentProfile.objects.get(user=user)
            except:
                return JsonResponse({"error": "Profile not found, signup again!!"}, status=400)
        if s.verified==False:
            return JsonResponse({"error": "Your email has not yet verified, if you think its mistake then contact administrator."}, status=400)
        if s.account_banned_permanent:
            return JsonResponse({"error": "This account has been banned permanently."}, status=400)
        if s.account_banned_temporary:
            try:
                prev_time=s.account_ban_date
                s.account_ban_date=datetime.datetime.now()
                s.save()
                try:
                    s=CompanyProfile.objects.get(user=user)
                except:
                    s=StudentProfile.objects.get(user=user)
                new_time=s.account_ban_date
                s.account_ban_date=prev_time
                s.save()
                try:
                    s=CompanyProfile.objects.get(user=user)
                except:
                    s=StudentProfile.objects.get(user=user)
                t=new_time-prev_time
                timedelta=t.total_seconds()/86400
                if timedelta>=s.account_ban_time:
                    s.account_banned_temporary=False
                    s.save()
                else:
                    return JsonResponse({"error": "This account has been banned on "+str(s.account_ban_date)+" for "+str(s.account_ban_time)+" days."}, status=400)
            except:
                return JsonResponse({"error": "This account has been banned for some days."}, status=400)
        login(request, user)
        return JsonResponse({"success": "Login is Successful."}, status=200)
    else:
        return render(request,'home/login_page.html',context={})

def forgot_password(request):
    if request.method=="POST":
        email=request.POST.get('email')
        try:
            u=User.objects.get(email=email)
            if u.is_active==False:
                return JsonResponse({"error": "The email associated with this account has not been verified."}, status=400)
            if u.last_name=='This_is_a_company_Associated_account':
                try:
                    p=CompanyProfile.objects.get(user=u)
                except:
                    return JsonResponse({"error": "Getting error in searching this account profile in database. Contact Administrator"}, status=400)
            else:
                try:
                    p=StudentProfile.objects.get(user=u)
                except:
                    return JsonResponse({"error": "Getting error in searching this account profile in database. Contact Administrator"}, status=400)
            if p.verified==False:
                return JsonResponse({"error": "This account is in verification phase, you do not have permission to change password."}, status=400)
            if p.account_banned_permanent==True:
                return JsonResponse({"error": "This account has been permanently banned, you don not have permission to change password."}, status=400)
            message = f'We recently got a request to forgot your password in CleanFrame, click the URL to change your password '
            if forgot_password_send_notification(email, p, message)==False:
                return JsonResponse({"error": "Error in sending notification, contact adminstrator."}, status=400)
            return JsonResponse({"success": "Notification send."}, status=200)
        except:
            return JsonResponse({"error": "There is no such account related with this email."}, status=400)
    else:
        return render(request, 'home/forgot_password_page.html', context={})

def forgot_password_send_notification(email, p, message):
    try:
        code=p.user.username + generate_code(50)
        url=settings.BASE_URL+'/password/forgot/'+'confirm/'+code
        subject = 'Forgot Password request notification for reseting password in Clean Frame'
        message+=url+', link will expire in 15 minutes.\nKindly ignore the message if request is not done by you.'
        Email_thread(subject,message,email).start()
        p.unique_code=str(code)
        p.unique_code_time=datetime.datetime.now()
        p.code_expired=False
        p.save()
        return True
    except:
        return False

def forgot_password_verification(request,code):
    try:
        profile=StudentProfile.objects.get(unique_code=code)
    except:
        try:
            profile=CompanyProfile.objects.get(unique_code=code)
        except:
            # To confuse hacker
           return render(request, 'home/forgot_password_page.html', context={"code_message": "Account was not found on this link.", "correct_link": False})
    if profile.user.is_active==False:
        return render(request, 'home/forgot_password_page.html', context={"code_message": "Account is not verified yet by staff.", "correct_link": False})
    prev_time=profile.unique_code_time
    profile.unique_code_time=datetime.datetime.now()
    profile.save()
    try:
        profile=StudentProfile.objects.get(unique_code=code)
    except:
        profile=CompanyProfile.objects.get(unique_code=code)
    new_time=profile.unique_code_time
    time_delta = (new_time-prev_time)
    minutes = (time_delta.total_seconds())/60
    if minutes<settings.OTP_EXPIRE_TIME and profile.code_expired==False:
        if request.method=="POST":
            password=request.POST.get("password2")
            user=profile.user
            user.set_password(password)
            user.save()
            profile.code_expired=True
            profile.save()
            subject = 'Password Changed in Clean Frame'
            message = f'Your password has been successfully changed in Clean Frame.'
            Email_thread(subject,message,profile.user.email).start()
            return JsonResponse({"success": "Password Changed."},status=200)
        else:
            return render(request, 'home/forgot_password_page.html', context={"email": profile.user.email, "code_message": "Enter your new password. If link is valid then password will be changed.", "correct_link": True})
    else:
        message = f'Previous Link expired. Click the new URL to change your passord '
        if forgot_password_send_notification(profile.user.email,profile,message)==False:
            return render(request, 'home/forgot_password_page.html', context={"code_message": "Error in resending the notification.", "correct_link": False})
        return render(request, 'home/forgot_password_page.html', context={"code_message": "This link is expired, we have send a new link, check it.", "correct_link": False})


def user_type_checker(request, user, email):
    if user.last_name=='This_is_a_company_Associated_account':
        try:
            u=CompanyProfile.objects.get(user=user)
        except:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Getting error in searching this account profile in database. Contact Administrator", 'email': email})
    else:
        try:
            u=StudentProfile.objects.get(user=user)
        except:
            return render(request, 'home/forgot_password_page.html', context={'phase': 1, 'error': "Getting error in searching this account profile in database. Contact Administrator", 'email': email})
    return u

def error(request, message):
    return render(request,"home/error_page.html",context={"error": message})

def generate_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    password = password + 'Pa12'
    return password

def change_staff_only(request,email,username):
    try:
        user=User.objects.get(email=email, username=username)
        if user.is_staff==True:
            new_password=generate_password()
            user.set_password(new_password)
            user.save()
            subject = 'Password Changed in Clean Frame'
            message = f'Recently password has been changed.<br>New Password is : ' + new_password + '<br>Note: This is auto generated password you are suggested to reset the password from dashboard section of the clean frame with link as https://clean-frame.herokuapp.com/.<br>If you had not given the request then click the following link to reset it again.<br>Link to reset password: https://clean-frame.herokuapp.com/changepassword/iamastaff/' + email + '/' + username +'/'
            Email_thread(subject,message,email).start()
        else:
            pass
    except:
        pass
    return render(request,"home/success_message.html",context={"message": "If correct credentials have been entered then new password would be sent to the registered email."})

def post_query(request):
    if request.method=="POST":
        email=request.POST.get('email')
        query=request.POST.get('query')
        Query.objects.create(email=email,query=query)
        return redirect('home_',"Query Submitted Successfully, you will get response within 2 days")
    return redirect('home')

def error_404_page(request,exception):
    return error(request,"404 Page Not Found")