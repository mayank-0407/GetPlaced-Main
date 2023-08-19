from django.http.response import JsonResponse
from django.core import serializers
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import (login,authenticate,logout)
from django.conf import settings
from django.core.mail import send_mail
import math,random,string,datetime
from twilio.rest import Client
from home.models import *
from .forms import *
from .models import *
from threading import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.contrib.staticfiles import finders
from functools import lru_cache
import pandas as pd
from background_task import background

class Email_thread(Thread):
    def __init__(self,subject,message,email):
        self.email=email
        self.subject=subject
        self.message=message
        Thread.__init__(self)

    def run(self):
        SENDMAIL(self.subject,self.message,self.email)

# Create your views here.
def SEND_OTP_TO_PHONE(mobile_number, country_code, message):
    client = Client(settings.PHONE_ACCOUNT_SID_TWILIO, settings.PHONE_ACCOUNT_AUTH_TOKEN_TWILIO)
    message = client.messages.create(
                        body=str(message),
                        from_= settings.PHONE_NUMBER_TWILIO,
                        to=str(country_code)+str(mobile_number)
                    )

def generate_otp():
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    OTP = ""
    for i in range(7) :
        OTP += digits[math.floor(random.random() * 62)]
    return OTP

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

def get_the_profile(user):
    data={}
    try:
        data=StudentProfile.objects.get(user=user)
    except:
        try:
            data=CompanyProfile.objects.get(user=user)
        except:
            data={}
    return data

def dashboard(request):
    if error_detection(request,1)==False:
        data=get_my_profile(request)
        if request.user.is_staff:
            staff = User.objects.filter(is_staff=True,is_superuser=False).count()
            admin = User.objects.filter(is_staff=True,is_superuser=True).count()
            company = User.objects.filter(is_staff=False,is_superuser=False,last_name=settings.COMPANY_MESSAGE).count()
            student = User.objects.filter(is_staff=False,is_superuser=False).count() - int(company)
            students_with_internship=StudentProfile.objects.filter(got_internship=True).count()
            return render(request,'dashboard1/dashboard_staff.html',context={"data": data, "staff_count": staff, "admin_count": admin, "company_count": company, "student_count": student, "permissions": get_permissions(request), "students_with_internship": students_with_internship})
        if request.user.last_name==settings.COMPANY_MESSAGE:
            user=CompanyProfile.objects.get(user=request.user).original_user
            internships_with_result=Internship.objects.filter(company=user, result_announced=True).count()
            internships_without_result=Internship.objects.filter(company=user, result_announced=False).count()
            internships=Internship.objects.filter(company=user)
            registrations=0
            for each in internships:
                registrations+=StudentRegistration.objects.filter(company__internship=each).count()
            selected_students=InternshipFinalResult.objects.filter(company=request.user).count()
            unselected_students=registrations-selected_students
            return render(request,'dashboard1/dashboard_company.html',context={"data": data, "internships_with_result": internships_with_result, "internships_without_result": internships_without_result, "selected_students": selected_students, "unselected_students": unselected_students, "internships": internships.count(), "registrations": registrations})
        else:
            my_registrations=StudentRegistration.objects.filter(student=request.user).count()
            my_selections=InternshipFinalResult.objects.filter(student=request.user).count()
            internships_accepted=InternshipFinalResult.objects.filter(student=request.user).count()
            internships_reverted=StudentRegistration.objects.filter(student=request.user, result_status=3).count()
            return render(request,'dashboard1/dashboard_student.html',context={"data": data, "my_registrations": my_registrations, "my_selections": my_selections, "internships_accepted": internships_accepted, "internships_reverted": internships_reverted})
    return error_detection(request,1)

def get_permissions(request):
    try:
        permissions = StaffPermissions.objects.get(user=request.user)
    except:
        StaffPermissions.objects.create(user=request.user)
        permissions = StaffPermissions.objects.get(user=request.user)
    return permissions

def error_code(request, message):
    return render(request,"home/error_code.html",context={"error": message})

def error_message(request, message):
    return render(request,"home/error_message.html",context={"error": message})

def error_detection(request,id):
    if request.user.is_authenticated==False:
        return redirect('home')
    if request.user.is_staff or request.user.is_superuser:
        return False
    if request.user.is_active==False:
        return error(request,"Your account is not yet been active.")
    if request.user.last_name==settings.COMPANY_MESSAGE:
        try:
            p=CompanyProfile.objects.get(user=request.user)
        except:
            return error(request,"Profile Not Found")
    else:
        try:
            p=StudentProfile.objects.get(user=request.user)
        except:
            return error(request,"Profile Not Found")
    if p.account_banned_permanent:
        logout(request)
        return error(request,"Your account is banned permanently")
    if p.account_banned_temporary:
        logout(request)
        return error(request,"Your account is banned temporarily, login again")
    if p.profile_filled==False and id==1:
        return redirect('profile')
    return False

def profile(request):
    if error_detection(request,2)==False:
        return profile_i(request,'')
    return error_detection(request,2)

def profile_i(request,error):
    contact_given=True
    try:
        p=StudentProfile.objects.get(user=request.user)
        contact_given=p.profile_filled
    except:
        try:
            p=CompanyProfile.objects.get(user=request.user)
            contact_given=p.profile_filled
        except:
            p={}
    data=get_my_profile(request)
    return render(request,'dashboard/profile.html',context={"contact_given": contact_given, "phase": 1, "data": p, "error": error, "permissions": get_permissions(request), "data": data, "SKIP_PHONE_NUMBER_FIELD_PROFILE": settings.SKIP_PHONE_NUMBER_FIELD_PROFILE})

def skip_profile_phonenumber(request):
    if not settings.SKIP_PHONE_NUMBER_FIELD_PROFILE:
        return redirect('dashboard')
    if request.user.is_authenticated:
        try:
            p=StudentProfile.objects.get(user=request.user)
            p.contact_number=""
            p.profile_filled=True
            p.save()
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
        except:
            try:
                p=CompanyProfile.objects.get(user=request.user)
                p.contact_number=""
                p.profile_filled=True
                p.save()
                data=get_my_profile(request)
                return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
            except Exception as e:
                print(e)
                return redirect('dashboard')
    else:
        return redirect('home')

def send_otp_to_phone_stu(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            phone_number=request.POST.get('contact_number')
            address=request.POST.get('address')
            gender=request.POST.get('gender')
            if StudentProfile.objects.filter(contact_number=str(phone_number),profile_filled=True).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if CompanyProfile.objects.filter(contact_number=str(phone_number),profile_filled=True).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if(otp_sender_to_student(request, phone_number)==False):
                return redirect('dashboard')
            try:
                p=StudentProfile.objects.get(user=request.user)
                p.contact_number=str(phone_number)
                p.complete_address=address
                if str(gender)=='1':
                    p.gender='Male'
                elif str(gender)=='2':
                    p.gender='Female'
                else:
                    p.gender='Transgender'
                p.save()
                data=get_my_profile(request)
                return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
            except Exception as e:
                print(e)
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def otp_sender_to_student(request, phone_number):
    try:
        user=User.objects.get(email=request.user.email)
    except:
        return False
    otp=str(generate_otp())
    try:
        SEND_OTP_TO_PHONE(phone_number,'+91',"OTP to verify phone number for the student account in Clean Frame is : " + str(otp) + ".\nDo not share it with anyone. It will expire in 15 minutes.")
    except:
        return error(request,"Unable to Send OTP to this phone number, contact Administrator")
    try:
        u=StudentProfile.objects.get(user=user)
        u.otp=str(otp)
        u.otp_time=datetime.datetime.now()
        u.save()
    except Exception as e:
        print(e)
        return False
    return True

def verify_otp_phone_stu(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            otp=request.POST.get('otp')
            try:
                user=request.user
                u=StudentProfile.objects.get(user=user)
                phone_number=u.contact_number
                data=get_my_profile(request)
                if str(otp)==str(u.otp):
                    prev_time=u.otp_time
                    u.otp_time=datetime.datetime.now()
                    u.save()
                    u=StudentProfile.objects.get(user=user)
                    new_time=u.otp_time
                    time_delta = (new_time-prev_time)
                    minutes = (time_delta.total_seconds())/60
                    if minutes<settings.OTP_EXPIRE_TIME:
                        try:
                            u=StudentProfile.objects.get(user=user)
                            u.otp='NULL_akad_bakad_bambe_bo'
                            if u.profile_filled==False:
                                u.profile_created=datetime.datetime.now()
                            u.profile_filled=True
                            u.save()
                            return render(request,'dashboard/profile.html',context={"phase": 3, "permissions": get_permissions(request), "data": data})
                        except:
                            return redirect('dashboard')
                    else:
                        if(otp_sender_to_student(request, phone_number)==False):
                            return redirect('dashboard')
                        return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP has been expired, we have sent a new OTP to phone number", "permissions": get_permissions(request), "data": data})
                else:
                    return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "Invalid OTP", "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def resend_otp_to_phone_stu(request):
    if request.user.is_authenticated:
        try:
            user=request.user
            u=StudentProfile.objects.get(user=user)
            phone_number=u.contact_number
            if(otp_sender_to_student(request, phone_number)==False):
                return redirect('dashboard')
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP sent again", "permissions": get_permissions(request), "data": data})
        except:
            return redirect('dashboard')
    else:
        return redirect('home')

def send_otp_to_phone_com(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            phone_number=request.POST.get('contact_number')
            address=request.POST.get('address')
            if StudentProfile.objects.filter(contact_number=str(phone_number),profile_filled=True).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if CompanyProfile.objects.filter(contact_number=str(phone_number),profile_filled=True).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if(otp_sender_to_company(request, phone_number)==False):
                return redirect('dashboard')
            try:
                p=CompanyProfile.objects.get(user=request.user)
                p.contact_number=str(phone_number)
                p.complete_address=address
                p.save()
                data=get_my_profile(request)
                return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def otp_sender_to_company(request, phone_number):
    try:
        user=User.objects.get(email=request.user.email)
    except:
        return False
    otp=str(generate_otp())
    try:
        SEND_OTP_TO_PHONE(phone_number,'+91',"OTP to verify phone number for the student account in Clean Frame is : " + str(otp) + ".\nDo not share it with anyone. It will expire in 15 minutes.")
    except:
        return error(request,"Unable to Send OTP to this phone number, contact Administrator")
    try:
        u=CompanyProfile.objects.get(user=user)
        u.otp=str(otp)
        u.otp_time=datetime.datetime.now()
        u.save()
    except:
        return False
    return True


def verify_otp_phone_com(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            otp=request.POST.get('otp')
            try:
                user=request.user
                u=CompanyProfile.objects.get(user=user)
                phone_number=u.contact_number
                data=get_my_profile(request)
                if str(otp)==str(u.otp):
                    prev_time=u.otp_time
                    u.otp_time=datetime.datetime.now()
                    u.save()
                    u=CompanyProfile.objects.get(user=user)
                    new_time=u.otp_time
                    time_delta = (new_time-prev_time)
                    minutes = (time_delta.total_seconds())/60
                    if minutes<settings.OTP_EXPIRE_TIME:
                        try:
                            u=CompanyProfile.objects.get(user=user)
                            u.otp='NULL_akad_bakad_bambe_bo'
                            if u.profile_filled==False:
                                u.profile_created=datetime.datetime.now()
                            u.profile_filled=True
                            u.save()
                            return render(request,'dashboard/profile.html',context={"phase": 3, "permissions": get_permissions(request), "data": data})
                        except:
                            return redirect('dashboard')
                    else:
                        if(otp_sender_to_company(request, phone_number)==False):
                            return redirect('dashboard')
                        return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP has been expired, we have sent a new OTP to phone number", "permissions": get_permissions(request), "data": data})
                else:
                    return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "Invalid OTP",  "permissions": get_permissions(request), "data": data})
            except:
                return redirect('dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('home')

def resend_otp_to_phone_com(request):
    if request.user.is_authenticated:
        try:
            user=request.user
            u=CompanyProfile.objects.get(user=user)
            phone_number=u.contact_number
            if(otp_sender_to_company(request, phone_number)==False):
                return redirect('dashboard')
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "error": "OTP sent again", "permissions": get_permissions(request), "data": data})
        except:
            return redirect('dashboard')
    else:
        return redirect('home')

def staff_profile(request):
    if request.user.is_authenticated and request.user.is_staff :
        if request.method=="POST":
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')
            u=User.objects.get(username=request.user)
            u.first_name=first_name
            u.last_name=last_name
            u.save()
            return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_profile_3(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            first_name=request.POST.get('first_name')
            last_name=request.POST.get('last_name')
            u=User.objects.get(username=request.user)
            u.first_name=first_name
            u.last_name=last_name
            u.save()
            address=request.POST.get('address')
            gender=request.POST.get('gender')
            try:
                p=StudentProfile.objects.get(user=request.user)
                p.complete_address=address
                if str(gender)=='1':
                    p.gender='Male'
                elif str(gender)=='2':
                    p.gender='Female'
                else:
                    p.gender='Transgender'
                p.save()
                return redirect('profile')
            except:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def company_profile_2(request):
    if request.user.is_authenticated :
        if request.user.last_name==settings.COMPANY_MESSAGE:
            com_name=request.POST.get('company_name')
            u=User.objects.get(username=request.user)
            u.first_name=com_name
            u.save()
            address=request.POST.get('address')
            try:
                p=CompanyProfile.objects.get(user=request.user)
                p.complete_address=address
                p.save()
                return redirect('profile')
            except:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def company_profile_3(request):
    if request.user.is_authenticated :
        if request.user.last_name==settings.COMPANY_MESSAGE:
            form = CompanyPhotoForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=CompanyProfile.objects.get(user=request.user)
                    image=request.POST.get("image")
                    if image!="":
                        # delete_image(profile.image)
                        profile.image=form.cleaned_data.get("image")
                        profile.save()
                    return redirect('profile')
                except:
                    return redirect('profile')
            else:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

# def delete_image(image):
#     if request.method == 'POST':
#         physical_files = set()
#         media_root = getattr(settings, 'MEDIA_ROOT', None)
#         # get all the files
#         if media_root is not None:
#             for relative_root, dirs, files in os.walk(media_root):
#                 for file_ in files:
#                     relative_file = os.path.join(os.path.relpath(relative_root, media_root), file_)
#                     physical_files.add(relative_file)
#         deletables = physical_files
#         if deletables:
#             for file_ in deletables:
#                 os.remove(os.path.join(media_root, file_))

#             # Bottom-up - delete all empty folders
#             for relative_root, dirs, files in os.walk(media_root, topdown=False):
#                 for dir_ in dirs:
#                     if not os.listdir(os.path.join(relative_root, dir_)):
#                         os.rmdir(os.path.join(relative_root, dir_))
#     return HttpResponse("Done")

def student_profile_2(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            form = StudentPhotoForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=StudentProfile.objects.get(user=request.user)
                    image=request.POST.get("image")
                    if image!="":
                        # delete_image(profile.image)
                        profile.image=form.cleaned_data.get("image")
                        profile.save()
                    return redirect('profile')
                except:
                    return redirect('profile')
            else:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_profile_1(request):
    if request.user.is_authenticated :
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            form = StudentCVForm(request.POST,request.FILES)
            if form.is_valid():
                try:
                    profile=StudentProfile.objects.get(user=request.user)
                    if form.cleaned_data.get("cv"):
                        profile.cv=form.cleaned_data.get("cv")
                        profile.save()
                    return redirect('profile')
                except:
                    return redirect('profile')
            else:
                return redirect('profile')
        else:
            return redirect('dashboard')
    else:
        return redirect('dashboard')

def student_company_number(request):
    if request.user.is_authenticated:
        if request.method=="POST":
            phone_number=request.POST.get('contact_number')
            if StudentProfile.objects.filter(contact_number=str(phone_number),profile_filled=True).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            if CompanyProfile.objects.filter(contact_number=str(phone_number),profile_filled=True).count() >= 1:
                return profile_i(request,'Account with given mobile number already exists')
            u=User.objects.get(username=request.user)
            if u.last_name==settings.COMPANY_MESSAGE:
                if(otp_sender_to_company(request, phone_number)==False):
                    return redirect('dashboard')
                p=CompanyProfile.objects.get(user=request.user)
            else:
                if(otp_sender_to_student(request, phone_number)==False):
                    return redirect('dashboard')
                p=StudentProfile.objects.get(user=request.user)
            p.contact_number=str(phone_number)
            p.profile_filled=False
            p.save()
            data=get_my_profile(request)
            return render(request,'dashboard/profile.html',context={"phase": 2, "phone": phone_number, "permissions": get_permissions(request), "data": data})
        else:
            return redirect('dashboard')
    else:
        return redirect('home')


def change_password(request):
    if error_detection(request,1)==False:
        try:
            profile=CompanyProfile.objects.get(user=request.user)
            if profile.engaged:
                return error(request,"You don't have permission to access this page")
        except:
            pass
        data=get_my_profile(request)
        if request.method=="POST":
            password=request.POST.get('password2')
            user=request.user
            user.set_password(password)
            user.save()
            subject = 'Password changed in Clean Frame'
            message = f'Password has been successfully changed.'
            Email_thread(subject,message,user.email).start()
            return redirect('dashboard')
        else:
            return render(request,'dashboard/change_password.html',context={ "permissions": get_permissions(request), "data": data})
    return error_detection(request,1)

def student_account_signup_permit(request):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_student_inactive_accounts==False:
            return redirect('dashboard')
        data=StudentProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data})
    return error_detection(request,1)

def student_account_signup_action(request,type,item):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_student_inactive_accounts==False:
            return redirect('dashboard')
        message__=""
        subject = 'Action taken on your signup request'
        code=0
        if type=="1":
            try:
                details=StudentProfile.objects.get(id=int(item))
                email=details.user.email
                if details.verified==True:
                    code=3
                else:
                    details.verified=True
                    details.save()
                    code=1
                    message = f'Your request for creating the account has been successfully met. You can login and register for internships'
                    Email_thread(subject,message,email).start()
            except:
                code=0
        elif type=="2":
            try:
                details=StudentProfile.objects.get(id=int(item))
                u=User.objects.get(username=details.user)
                email=details.user.email
                if details.verified==True:
                    code=4
                else:
                    u.delete()
                    code=2
                    message = f'Your request for creating the account has been blocked and your account has been deleted. This may due to some inapropriate data given in the signup form.<br/>You can register again on the clean frame. Be sure this time, you give correct details, otherwise the email can be blocked permanently.'
                    Email_thread(subject,message,email).start()
            except:
                code=0
        data=StudentProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data, "code": code})
    return error_detection(request,1)

def company_account_signup_permit(request):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_company_inactive_accounts==False:
            return redirect('dashboard')
        data=CompanyProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        return render(request,'dashboard/company_accounts.html',context={ "permissions": get_permissions(request), "data": data})
    return error_detection(request,1)

def company_account_signup_action(request,type,item):
    if error_detection(request,1)==False:
        permissions=get_permissions(request)
        if permissions.can_access_company_inactive_accounts==False:
            return redirect('dashboard')
        message__=""
        subject = 'Action taken on your signup request'
        code=0
        if type=="1":
            try:
                details=CompanyProfile.objects.get(id=int(item))
                email=details.user.email
                if details.verified==True:
                    code=3
                else:
                    details.verified=True
                    details.save()
                    code=1
                    message = f'Your request for creating the account has been successfully met. You can login and register for internships'
                    Email_thread(subject,message,email).start()
            except:
                code=0
        elif type=="2":
            try:
                details=CompanyProfile.objects.get(id=int(item))
                u=User.objects.get(username=details.user)
                email=details.user.email
                if details.verified==True:
                    code=4
                else:
                    u.delete()
                    code=2
                    message = f'Your request for creating the account has been blocked and your account has been deleted. This may due to some inapropriate data given in the signup form.<br/>You can register again on the clean frame. Be sure this time, you give correct details, otherwise the email can be blocked permanently.'
                    Email_thread(subject,message,email).start()
            except:
                code=0
        data=CompanyProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        return render(request,'dashboard/company_accounts.html',context={ "permissions": get_permissions(request), "data": data, "code": code})
    return error_detection(request,1)

def SENDMAIL(subject, message, email):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    checker = User.objects.get(email=email)
    username = checker.username
    html_content = render_to_string("home/email.html",{'message': message, 'user_name': username})
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject,text_content,email_from,recipient_list)
    email.attach_alternative(html_content,"text/html")
    email.send()
    # return render(request,'home/email.html',{'title':'send an email'})
    # send_mail( subject, message, email_from, recipient_list )


def new_announcement_round(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        internships=Internship.objects.filter(company=data.original_user, session=current_session())
        prev_round_for_result=0
        if request.method == "POST":
            internship_name=request.POST.get('internship_name')
            internship_round=int(request.POST.get('internship_round'))
            try:
                int_obj=Internship.objects.get(id=int(internship_name))
                CompanyAnnouncement.objects.get(company=data.original_user, internship_round=internship_round, internship=int_obj)
                return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "This round has been already declared"})
            except:
                pass
            if(internship_round>1):
                prev_round_for_result=request.POST.get('prev_round_for_result')
                try:
                    c=CompanyAnnouncement.objects.get(company=data.original_user, internship_round=prev_round_for_result, internship=int_obj)
                except:
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "No announcement found with the given previous round number"})
                if c.last_round==True:
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "Final Round of this internship has been announced"})
                if(StudentRegistration.objects.filter(company=c, result_status=1).count()<=0):
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "No student found whose previous round was cleared"})
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                internship=Internship.objects.get(id=int(internship_name))
                if internship.session!=current_session():
                    return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": "You can only choose an internship with active session"})
                x=form.save()
                myid=x.id
                last_date_to_apply=request.POST.get('last_date_to_apply')
                com_ann=CompanyAnnouncement.objects.get(id=myid)
                com_ann.company=data.original_user
                last_round=request.POST.get("last_round")
                if int(last_round)==2:
                    com_ann.last_round=True
                if internship_round==1:
                    com_ann.first_round=True
                    com_ann.prev_round_for_result=0
                if len(last_date_to_apply) > 1 :
                    com_ann.last_date_to_apply=datetime.datetime.strptime(str(last_date_to_apply), '%Y-%m-%dT%H:%M')
                com_ann.internship=Internship.objects.get(id=int(internship_name))
                com_ann.save()
                if internship_round!=1:
                    com_ann=CompanyAnnouncement.objects.get(id=myid)
                    prev_ann=CompanyAnnouncement.objects.get(company=data.original_user, internship_round=prev_round_for_result, internship=int_obj)
                    register_students_for_next_round(request, prev_ann, com_ann)
                    notify_other_students_for_rejection(request, prev_ann, com_ann)
                return redirect('new_announcement_success', '1')
            else:
                return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships, "error": form.errors})
        else:
            internships=Internship.objects.filter(company=data.original_user, session=current_session())
            return render(request, 'dashboard/new_round.html', context={"data": data, "internships": internships})
    return error_detection(request,1)

def register_students_for_next_round(request, prev, new):
    get_students=StudentRegistration.objects.filter(company=prev, result_status=1)
    for each in get_students:
        each.company=new
        each.result_status=0
        each.save()
        subject = 'Registration for next Round'
        message = f'You have been successfully registered for next round of internship.<br/>Details of this round are as follows:<br/>Company Name: '+str(each.company.company.first_name)+'<br/>Internship Name: '+str(each.company.internship.internship_name)+'<br/>Round Number: '+str(each.company.internship_round)
        email=each.student.email
        Email_thread(subject,message,email).start()

def notify_other_students_for_rejection(request, prev, new):
    get_students=StudentRegistration.objects.filter(company=prev, result_status=0)
    for each in get_students:
        each.result_status=2
        each.save()
        subject = 'Internship Round Result'
        message = f'We are sorry for telling you that you have been rejected in an internship round.<br/>Details of this round are as follows:<br/>Company Name: '+str(each.company.company.first_name)+'<br/>Internship Name: '+str(each.company.internship.internship_name)+'<br/>Round Number: '+str(each.company.internship_round)
        email=each.student.email
        Email_thread(subject,message,email).start()

def new_announcement_success(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        else:
            data=get_my_profile(request)
            internships=Internship.objects.filter(company=data.original_user)
            if item=='1':
                return render(request, 'dashboard/new_round.html', context={"data": data, "success": "Announcement Created", "internships": internships})
            if item=='2':
                return render(request, 'dashboard/new_announcement.html', context={"data": data, "success": "Announcement Created", "internships": internships})
            else:
                return error(request,"Page Not Found")
    return error_detection(request,1)

def announce_internship(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        else:
            data=get_my_profile(request)
            session=current_session()
            if request.method=="POST":
                duration=request.POST.get('duration')
                intern_pos=request.POST.get('internship_position')
                min_cgpa=request.POST.get('minimum_cgpa')
                stipend=request.POST.get('stipend')
                pre=request.POST.get('pre')
                internship_name=request.POST.get('internship_name')
                try:
                    Internship.objects.get(session=session, company=data.original_user, internship_name=internship_name, stipend=stipend, internship_duration=duration, internship_position=intern_pos, minimum_cgpa=min_cgpa, prerequisite=pre)
                    return JsonResponse({"error": "Internship with same details already exists"}, status=400)
                except:
                    Internship.objects.create(session=session, company=data.original_user, internship_name=internship_name, stipend=stipend, internship_duration=duration, internship_position=intern_pos, minimum_cgpa=min_cgpa, prerequisite=pre)
                    return JsonResponse({"success": "internship created"}, status=200)
            # GO FOR GET METHOD
            return render(request, 'dashboard/new_internship.html', context={"data": data, "session": session})
    return error_detection(request,1)

def announcements(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        announcements=CompanyAnnouncement.objects.filter(company=CompanyProfile.objects.get(user=request.user).original_user).order_by('announcement_date')
        internships=Internship.objects.filter(company=CompanyProfile.objects.get(user=request.user).original_user)
        return render(request, 'dashboard/announcements.html', context={"announcements": announcements, "internships": internships})
    return error_detection(request,1)

def internships(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        internships=Internship.objects.filter(company=CompanyProfile.objects.get(user=request.user).original_user)
        sessions=Session.objects.all().order_by('-active')
        return render(request, 'dashboard/internships.html', context={"internships": internships,"sessions": sessions})
    return error_detection(request,1)

def edit_internship(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        if request.method=="POST":
            try:
                data=Internship.objects.get(id=int(item))
                if data.company!=CompanyProfile.objects.get(user=request.user).original_user:
                    return JsonResponse({"error": "Internship Not Found"}, status=400)
                data.internship_name=request.POST.get('internship_name')
                data.internship_duration=int(request.POST.get('duration'))
                data.internship_position=request.POST.get('internship_position')
                data.minimum_cgpa=float(request.POST.get('minimum_cgpa'))
                data.stipend=float(request.POST.get('stipend'))
                data.prerequisite=request.POST.get('pre')
                data.save()
                return JsonResponse({"success": "Internship Details Updated"}, status=200)
            except:
                return JsonResponse({"error": "Error in details entered by you or Announcement not found"}, status=400)
        else:
            try:
                data=Internship.objects.get(id=int(item))
                if data.company!=CompanyProfile.objects.get(user=request.user).original_user:
                    return error(request,"Internship not found")
            except:
                return error(request,"Internship not found")
            return render(request, 'dashboard/edit_internships.html', context={"data": data})
    return error_detection(request,1)

def edit_announcement(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        if request.method=="POST":
            data=CompanyAnnouncement.objects.get(id=int(item))
            if data.company!=CompanyProfile.objects.get(user=request.user).original_user:
                return error(request,"Announcement not found")
            internship_round=int(request.POST.get('internship_round'))
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                data.internship_round=form.cleaned_data['internship_round']
                data.round_name=form.cleaned_data['round_name']
                data.prev_round_for_result=form.cleaned_data['prev_round_for_result']
                data.message=form.cleaned_data['message']
                if form.cleaned_data['file']:
                    data.file=form.cleaned_data['file']
                if form.cleaned_data['file_for_prev_result']:
                    data.file_for_prev_result=form.cleaned_data['file_for_prev_result']
                if data.first_round==True:
                    last_date_to_apply=request.POST.get('last_date_to_apply')
                if data.general_announcement==False and data.first_round==True:
                    data.last_date_to_apply=datetime.datetime.strptime(str(last_date_to_apply), '%Y-%m-%dT%H:%M')
                if data.internship_round==1:
                    data.first_round=True
                    data.prev_round_for_result=0
                data.save()
                return redirect('edit_announcement', int(item))
            else:
                return render(request, 'dashboard/edit_announcements.html', context={"data": data, "error": form.errors})

        else:
            try:
                data=CompanyAnnouncement.objects.get(id=int(item))
                if data.company!=CompanyProfile.objects.get(user=request.user).original_user:
                    return error(request,"Announcement not found")
            except:
                return error(request,"Announcement not found")
            return render(request, 'dashboard/edit_announcements.html', context={"data": data})
    return error_detection(request,1)

def new_announcement(request):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if request.method == "POST":
            form = CompanyAnnouncementForm(request.POST,request.FILES)
            if form.is_valid():
                x=form.save()
                com_ann=CompanyAnnouncement.objects.get(id=x.id)
                com_ann.company=data.original_user
                com_ann.general_announcement=True
                com_ann.save()
                return redirect('new_announcement_success', '2')
            else:
                return render(request, 'dashboard/new_announcement.html', context={"data": data, "error": form.errors})
        else:
            return render(request, 'dashboard/new_announcement.html', context={"data": data})
    return error_detection(request,1)

def students_result_file_upload(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        if request.method == "POST":
            try:
                data=CompanyAnnouncement.objects.get(id=int(item))
            except:
                return error(request,"Announcement Not Found")
            if data.company!=CompanyProfile.objects.get(user=request.user).original_user:
                return error(request,"Announcement Not Found")
            announcement=data
            form=NewUserForm(request.POST,request.FILES)
            if form.is_valid():
                file=form.cleaned_data.get('file')
                if str(file).endswith('.csv'):
                    # csv file
                    data=pd.read_csv(file)
                elif str(file).endswith('.xlsx'):
                    # excel file
                    data=pd.read_excel(file)
                else:
                    students=get_students(request, announcement)
                    return render(request, 'dashboard/result.html', context={"data": announcement, "students": students, "error": 'Not an excel or csv file'})     
                return students_result_file_upload_helper(request,data,announcement)
            students=get_students(request, announcement)
            return render(request, 'dashboard/result.html', context={"data": announcement, "students": students, "error": str(form.errors)})
        else:
            return redirect('dashboard')
    return error_detection(request,1)

def students_result_file_upload_helper(request,data,announcement):
    students=get_students(request, announcement)
    email_given=False
    status_given=False
    if 'Email' not in data.columns and 'Username' not in data.columns:
        return render(request, 'dashboard/result.html', context={"data": announcement, "students": students, "error": 'Email or Username column was not found in the file.'})     
    if 'Email' in data.columns:
        email_given=True
    if 'Result Status' in data.columns:
        status_given=True

    field_on_operation=0
    if email_given:
        field_on_operation=data['Email']
    else:
        field_on_operation=data['Username']

    field_with_unknown_values=[]
    field_with_student_not_found=[]
    for i in range(len(field_on_operation)):
        field=field_on_operation[i]
        result_status=1
        if status_given:
            if data["Result Status"][i]=="Fail":
                result_status=2
        if field:
            try:
                user=0
                if email_given:
                    user=User.objects.get(email=field)
                else:
                    user=User.objects.get(username=field)
                if user.is_staff or user.is_superuser or user.last_name==settings.COMPANY_MESSAGE:
                    field_with_student_not_found.append(i+1)
                else:
                    try:
                        get_re=StudentRegistration.objects.get(student=user, company=announcement)  
                        if get_re.result_status==0:
                            get_re.result_status=result_status
                            get_re.save()
                            if result_status==1:
                                subject = 'Internship Round Cleared'
                                message = f'We congratulate you for clearing the round in internship.<br/>Details of cleared round are as follows:<br/>Company Name: '+str(get_re.company.company.first_name)+'<br/>Internship Name: '+str(get_re.company.internship.internship_name)+'<br/>Round Number: '+str(get_re.company.internship_round)
                                Email_thread(subject,message,get_re.student.email).start()  
                            else:
                                subject = 'Internship Round Result'
                                message = f'We feel apology telling you that you have been rejected in an internship round.<br/>Details of this round are as follows:<br/>Company Name: '+str(get_re.company.company.first_name)+'<br/>Internship Name: '+str(get_re.company.internship.internship_name)+'<br/>Round Number: '+str(get_re.company.internship_round)
                                Email_thread(subject,message,get_re.student.email).start()  
                    except:
                        pass
            except:
                field_with_student_not_found.append(i+1)
        else:
            field_with_unknown_values.append(i+1)
    students=get_students(request, announcement)
    if len(field_with_unknown_values)==0 and len(field_with_student_not_found)==0:
        return render(request, 'dashboard/result.html', context={"data": announcement, "students": students, "success": "Results uploaded successfully."})
    elif len(field_with_unknown_values)==0:
        error="Rows in which student account was not found or this student never registered are : "+str(field_with_student_not_found)+" . You can cross-verify, results uploaded for the rest of the rows."
    elif len(field_with_student_not_found)==0:
        error="Rows with empty email or empty username or undefined result status are : "+str(field_with_unknown_values)+" . You can cross-verify, results uploaded for the rest of the rows."
    else:
        error1="Rows in which student account not found are : "+str(field_with_student_not_found)+" ."
        error2="Rows with empty email or empty username or undefined account type are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, results uploaded for the rest of the rows."
        error=error1+"\n"+error2
    return render(request, 'dashboard/result.html', context={"data": announcement, "students": students, "error": error})

def stu_result(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            data=CompanyAnnouncement.objects.get(id=int(item))
        except:
            return error(request,"Announcement Not Found")
        if data.company!=CompanyProfile.objects.get(user=request.user).original_user:
            return error(request,"Announcement Not Found")
        if request.method == "POST":
            students=request.POST.get("students")
            if len(students)<=3:
                return redirect('stu_result', item)
            spliter=students.split('**')
            mylist=spliter[0].split(",")
            if int(spliter[1])==1:
                for each_id in mylist:
                    get_re=StudentRegistration.objects.get(student=int(each_id), company=int(item))
                    if get_re.result_status!=1:
                        get_re.result_status=1
                        get_re.save()
                        subject = 'Internship Round Cleared'
                        message = f'We congratulate you for clearing the round in internship.<br/>Details of cleared round are as follows:<br/>Company Name: '+str(get_re.company.company.first_name)+'<br/>Internship Name: '+str(get_re.company.internship.internship_name)+'<br/>Round Number: '+str(get_re.company.internship_round)
                        email=get_re.student.email
                        Email_thread(subject,message,email).start()
                return redirect('stu_result', item)
            if int(spliter[1])==2:
                for each_id in mylist:
                    get_re=StudentRegistration.objects.get(student=int(each_id), company=int(item))
                    if get_re.result_status==0:
                        get_re.result_status=2
                        get_re.save()
                        subject = 'Internship Round Result'
                        message = f'We feel apology telling you that you have been rejected in an internship round.<br/>Details of this round are as follows:<br/>Company Name: '+str(get_re.company.company.first_name)+'<br/>Internship Name: '+str(get_re.company.internship.internship_name)+'<br/>Round Number: '+str(get_re.company.internship_round)
                        email=get_re.student.email
                        Email_thread(subject,message,email).start()
                return redirect('stu_result', item)
            return error(request,"INVALID REQUEST")
        else:
            students=get_students(request, data)
            return render(request, 'dashboard/result.html', context={"data": data, "students": students})
    return error_detection(request,1)

def internship_result(request,item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            internship=Internship.objects.get(id=int(item))
        except:
            return error(request,"Result Not Found")
        if internship.company!=CompanyProfile.objects.get(user=request.user).original_user:
            return error(request,"Announcement Not Found")
        students=InternshipFinalResult.objects.filter(internship=internship)
        data=get_my_profile(request)
        return render(request, 'dashboard/internship_result.html', context={"students": students})
    return error_detection(request,1)

#TO be COmpleted
def get_students(request, announcement):
    name=announcement.internship
    get_stu=StudentRegistration.objects.filter(company__internship=name)
    return get_stu

def show_companies(request):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        eligible_companies=all_announcements_with_my_eligibility(request)
        return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies})
    return error_detection(request,1)

def all_announcements_with_my_eligibility(request):
    eligible_companies=CompanyAnnouncement.objects.filter(general_announcement=False, first_round=True, last_date_to_apply__gte=datetime.datetime.now()).order_by('-announcement_date')
    copy=eligible_companies
    data=get_my_profile(request)
    final_list=[]
    for each in copy:
        dictionary={}
        dictionary["data"]=each
        dictionary["eligibility"]=True

        if each.internship.session!=current_session():
            dictionary["session_expired"]=True
            dictionary["eligibility"]=False
            final_list.append(dictionary)
            continue

        if each.last_round==True:
            if each.last_round_result_announced==True:
                dictionary["final_result_announced"]=True
                dictionary["eligibility"]=False
                final_list.append(dictionary)
                continue
        try:
            min_cgpa=each.internship.minimum_cgpa
            if data.cgpa<min_cgpa:
                dictionary["low_cgpa"]=True
                dictionary["eligibility"]=False
                final_list.append(dictionary)
                continue
            else:
                internship=each.internship
                all_ann=CompanyAnnouncement.objects.filter(internship=internship, first_round=True)[0]
                try:
                    StudentRegistration.objects.get(student=request.user, company=all_ann)
                    dictionary["already_registered"]=True
                    dictionary["eligibility"]=False
                    final_list.append(dictionary)
                    continue
                except:
                    pass
        except:
            continue
        try:
            CompanyAnnouncement.objects.get(internship=each.internship, company=each.company, internship_round=2)
            dictionary["result_announced"]=True
            dictionary["eligibility"]=False
            final_list.append(dictionary)
            continue
        except:
            pass
        final_list.append(dictionary)
    return final_list

def show_company_round_details(request, item):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            data1_is=True
            data=CompanyAnnouncement.objects.get(id=int(item))
            try:
                data2_is=True
                company_data=CompanyProfile.objects.get(user=data.company)
            except:
                data2_is=False
                company_data={}
        except:
            data1_is=False
            data2_is=False
            data={}
            company_data={}
        return render(request, 'dashboard/show_company_details.html', context={"announcement_data": data, "company_data": company_data, "data1": data1_is, "data2": data2_is})
    return error_detection(request,1)

def register_student_first_round_only(request, item):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        eligible_companies=all_announcements_with_my_eligibility(request)
        if data.got_internship==True:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "You can't register for internships this session because you already have one"})
        try:
            ann=CompanyAnnouncement.objects.get(id=int(item))
            s_data=StudentProfile.objects.get(user=request.user)
        except:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "Error in fetching your profile or announcement not found"})
        if ann.first_round==False:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "Announcement Round is not 1, contact staff to see into this matter."})
        if s_data.cgpa<ann.internship.minimum_cgpa:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "Your aren't eligible to register for this company since your CGPA does not met minimum CGPA set by the company"})
        if ann.internship.session.active==False:
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "No more registraions are allowed for the session in which you are trying to register."})
        try:
            StudentRegistration.objects.get(student=request.user, company=ann)
            return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "error": "You are Already registered"})
        except:
            try:
                ProfilePermissions.objects.get(user_who_can_see=ann.company,user_whose_to_see=request.user)
            except:
                ProfilePermissions.objects.create(user_who_can_see=ann.company,user_whose_to_see=request.user)
            StudentRegistration.objects.create(student=request.user, company=ann)
        data=get_my_profile(request)
        eligible_companies=all_announcements_with_my_eligibility(request)
        return render(request, 'dashboard/show_companies.html', context={"data": data, "companies": eligible_companies, "success": True})
    return error_detection(request,1)

#Unusable function but can be used to get exaclty those companies where I can apply.
def get_eligible_companies_for_me_round_one(request):
    eligible_companies=CompanyAnnouncement.objects.filter(general_announcement=False, first_round=True, last_date_to_apply__gte=datetime.datetime.now(), internship__session__active=True)
    copy=eligible_companies
    data=get_my_profile(request)
    for each in copy:
        if each.last_round==True:
            if each.last_round_result_announced==True:
                eligible_companies=eligible_companies.exclude(id=each.id)
                continue
        try:
            min_cgpa=each.internship.minimum_cgpa
            if data.cgpa<min_cgpa:
                eligible_companies=eligible_companies.exclude(id=each.id)
            else:
                internship=each.internship
                all_ann=CompanyAnnouncement.objects.filter(internship=internship)
                for i in all_ann:
                    try:
                        sr=StudentRegistration.objects.get(student=request.user, company=i)
                        eligible_companies=eligible_companies.exclude(id=each.id)
                        break
                    except:
                        continue
        except:
            eligible_companies=eligible_companies.exclude(id=each.id)
        try:
            next_round=CompanyAnnouncement.objects.get(internship=each.internship, company=each.company, internship_round=2)
            eligible_companies=eligible_companies.exclude(id=each.id)
        except:
            pass
    return eligible_companies

def show_registrations(request):
    if error_detection(request,1)==False:
        if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
            return redirect('home')
        data=get_my_profile(request)
        registrations=StudentRegistration.objects.filter(student=request.user)
        #Also get registrations of other rounds
        session=current_session()
        return render(request, "dashboard/registrations.html", context={"registrations": registrations, "session": session})
    return error_detection(request,1)

#This feature was in older version where student can take any action on an internship final round.
# def internship_action(request,item,type):
#     if error_detection(request,1)==False:
#         if request.user.is_staff or request.user.is_superuser or request.user.last_name==settings.COMPANY_MESSAGE:
#             return redirect('home')
#         data=get_my_profile(request)
#         try:
#             registration=StudentRegistration.objects.get(id=int(item))
#         except:
#             return error(request,"Registration not found")
#         if request.user!=registration.student:
#             return error(request,"Registration not found")
#         if registration.result_status!=1 or registration.internship_cleared==False:
#             return error(request,"May be this is not you are looking for.")
#         try:
#             company_announcement=registration.company
#             internship=registration.company.internship
#         except:
#             return error(request,"Internship not found")
#         if company_announcement.last_round==False or company_announcement.last_round_result_announced==False:
#             return error(request,"Not a last round or final results have not been seized")
#         if internship.result_announced==False:
#             return error(request,"Result of this internship has not been announced")
#         try:
#             internship_result=InternshipFinalResult.objects.filter(internship=internship, student=request.user)
#         except:
#             return error(request,"Internship Result not found")
#         if internship_result.count()!=1:
#             return error(request,"More than 1 resuls found for this, can\'t fetch which to take")
#         if internship_result[0].student_agrees==0:
#             if int(type)==2:
#                 result=internship_result[0]
#                 result.student_agrees=1
#                 result.save()
#                 registration.my_action=1
#                 registration.save()
#                 subject = 'Reverted Back'
#                 message = f'You have reverted back your selection in the internship which can\'t be undone, you can try for another interships.<br/>Details of this internship round are as follows:<br/>Company Name: '+str(registration.company.company.first_name)+'<br/>Internship Name: '+str(registration.company.internship.internship_name)+'<br/>Round Number: '+str(registration.company.internship_round)+' (last Round)'
#                 email=request.user.email
#                 Email_thread(subject,message,email).start()
#                 return redirect('show_registrations')
#             elif int(type)==1:
#                 result=internship_result[0]
#                 result.student_agrees=2
#                 result.save()
#                 registration.my_action=2
#                 registration.save()
#                 subject = 'Congratulations! intern'
#                 message = f'You have have been sucessfully selected for the internship, we congratulate for being an intern.<br/>Note: According to one student one company policy you can\'t regitser for other internships now.<br/>Details of this internship are as follows:<br/>Company Name: '+str(registration.company.company.first_name)+'<br/>Internship Name: '+str(registration.company.internship.internship_name)
#                 email=request.user.email
#                 Email_thread(subject,message,email).start()
#                 my_registrations=StudentRegistration.objects.filter(student=request.user)
#                 my_registrations=my_registrations.exclude(id=int(item))
#                 for each in my_registrations:
#                     each.result_status=3
#                     each.save()
#                 profile=get_my_profile(request)
#                 profile.got_internship=True
#                 profile.save()
#                 return redirect('show_registrations')
#             else:
#                 return error(request,"Page not found")
#         else:
#             return error(request,"You have already taken an action which can\'t be undone")
#     return error_detection(request,1)

def delete_internship(request,item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            inter=Internship.objects.get(id=int(item))
            if inter.company==CompanyProfile.objects.get(user=request.user).original_user:
                inter.delete()
                return redirect('internships')
            else:
                return error(request,"This account has no Permission to delete it")
        except:
            return error(request,"Internship Details not found")
    return error_detection(request,1)


def seeze_results(request,item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            comann=CompanyAnnouncement.objects.get(id=int(item))
            if comann.company!=CompanyProfile.objects.get(user=request.user).original_user:
                return error(request,"Announcement Details not found")
            if comann.last_round==False:
                return error(request,"Not a last round")
            internship=comann.internship
            if internship.result_announced==True:
                return error(request,"Final Result has been announced")
            accept_discard_students(request,comann)
            return redirect('stu_result',item)
        except:
            return error(request,"Announcement Details not found")
    return error_detection(request,1)

def accept_discard_students(request,announcement):
    internship=announcement.internship
    company=CompanyProfile.objects.get(user=request.user).original_user
    registrations=StudentRegistration.objects.filter(company=announcement)
    for each in registrations:
        profile=StudentProfile.objects.get(user=each.student)
        if each.result_status==1 and profile.got_internship==False:
            profile.got_internship=True
            profile.save()
            each.internship_cleared=True
            each.save()
            try:
                InternshipFinalResult.objects.get(internship=internship, company=company, student=each.student)
            except:
                InternshipFinalResult.objects.create(internship=internship, company=company, student=each.student)
            my_registrations=StudentRegistration.objects.filter(student=each.student, company__internship__session=current_session())
            for e in my_registrations:
                if e.company!=each.company:
                    e.result_status=3
                    e.save()
            subject = 'Congratulations! intern'
            message = f'You have have been sucessfully selected for the internship, we congratulate for being an intern.<br/>Note: According to one student one company policy you can\'t regitser for other internships now.<br/>Details of this internship are as follows:<br/>Company Name: '+str(each.company.company.first_name)+'<br/>Internship Name: '+str(each.company.internship.internship_name)
            email=each.student.email
            Email_thread(subject,message,email).start()
        if each.result_status==0:
            each.result_status=2
            each.save()
            subject = 'Internship Result Last Round'
            message = f'You have been rejected in the last round of internship, you can try for another interships.<br/>Details of this round are as follows:<br/>Company Name: '+str(each.company.company.first_name)+'<br/>Internship Name: '+str(each.company.internship.internship_name)+'<br/>Round Number: '+str(each.company.internship_round)+' (last Round)'
            email=each.student.email
            Email_thread(subject,message,email).start()
    all_ann=CompanyAnnouncement.objects.filter(internship=internship, company=company)
    for each in all_ann:
        each.last_round_result_announced=True
        each.save()
    internship.result_announced=True
    internship.save()


def delete_announcement(request, item):
    if error_detection(request,1)==False:
        if request.user.last_name!=settings.COMPANY_MESSAGE:
            return redirect('home')
        try:
            comann=CompanyAnnouncement.objects.get(id=int(item))
            if comann.company!=CompanyProfile.objects.get(user=request.user).original_user:
                return error(request,"Announcement Details not found")
            previous_round = comann.prev_round_for_result
            round_no=int(comann.internship_round)
            if comann.company==CompanyProfile.objects.get(user=request.user).original_user:
                if comann.last_round==True and comann.last_round_result_announced==True:
                    return error(request,"This Announcement can't be deleted because its results are seized")
                if round_no > 1:
                    try:
                        internship = comann.internship
                        abcd = CompanyAnnouncement.objects.filter(internship = internship)
                        # mx=0
                        # for each in abcd:
                        #     mx=get_max(int(mx),int(each.internship_round))
                        # if mx==int(comann.internship_round):
                        set_results_for_previous_round(request, int(previous_round), int(comann.internship_round), comann.internship)
                    except:
                        pass
                comann.delete()
                return redirect('announcements')
            else:
                return error(request,"This account has no Permission to delete it")
        except:
            return error(request,"Announcement Details not found")
    return error_detection(request,1)

def set_results_for_previous_round(request, old, new, internship):
    students = StudentRegistration.objects.filter(company__internship = internship)
    while old > 0:
        try:
            old_announcement = CompanyAnnouncement.objects.get(internship = internship, internship_round = str(old))
            break
        except:
            old=old-1
    if old==0:
        return
    for each in students:
        if each.company.internship_round == str(new):
            each.result_status = 1
            each.company = old_announcement
            each.save()
            subject = 'Reverted back for previous Round'
            message = f'You have been reverted back to previous round of internship because company deleted the latest round.<br/>Details of the current cleared round are as follows:<br/>Company Name: '+str(each.company.company.first_name)+'<br/>Internship Name: '+str(each.company.internship.internship_name)+'<br/>Round Number: '+str(each.company.internship_round)
            email=each.student.email
            Email_thread(subject,message,email).start()


def get_max(a,b):
    if a>b:
        return a
    return b

def check_student_profile(request, item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
            data=get_passed_profile(user_profile)
            if data=={}:
                return error(request,"Profile Not Found")
        except:
            return error(request,"Profile Not Found")
        if user_profile.last_name==settings.COMPANY_MESSAGE or user_profile.is_staff or user_profile.is_superuser:
            return error(request,"Profile Not Found")

        if request.method=="POST":
            permission=int(request.POST.get('profile_visibility'))
            user_id=int(request.POST.get('user_id'))
            try:
                user=User.objects.get(id=user_id)
            except:
                return error(request,"User not found")
            if request.user!=user:
                return error(request,"User Profile is Hidden")
            try:
                per=ProfileVisibility.objects.get(user=request.user)
            except:
                per=ProfileVisibility.objects.create(user=request.user)
                per.save()
            per.to_registered_companies=False
            per.to_all_companies=False
            per.to_all_students=False
            per.to_all=False
            if permission==1:
                per.to_registered_companies=True
            elif permission==2:
                per.to_all_companies=True
            elif permission==3:
                per.to_all_students=True
            elif permission==4:
                per.to_all=True
            per.save()
            return redirect('check_student_profile',request.user.id)
        try:
            my_permissions=ProfileVisibility.objects.get(user=user_profile)
            if request.user.is_staff==False:
                if check_profilepage_permissions(request, item) == False:
                    return error(request,"You do not not permission to view this user's profile page")
        except:
            ProfileVisibility.objects.create(user=user_profile, to_all=True)
            my_permissions=ProfileVisibility.objects.get(user=user_profile)
        image=data.image
        return render(request,'dashboard/profile_page_student.html',context={"data": data, "image": image, "permissions": my_permissions})
    return error_detection(request,1)

def check_profilepage_permissions(request, item):
    try:
        user_profile=User.objects.get(id=int(item))
        my_permissions=ProfileVisibility.objects.get(user=user_profile)
    except:
        return False
    if request.user == user_profile:
        return True
    else:
        try:
            ProfilePermissions.objects.get(user_who_can_see=request.user,user_whose_to_see=user_profile)
            return True
        except:
            if my_permissions.to_all==True:
                return True
            if my_permissions.to_all_students==True:
                if request.user.last_name!=settings.COMPANY_MESSAGE:
                    return True
            if my_permissions.to_all_companies==True:
                if request.user.last_name==settings.COMPANY_MESSAGE:
                    return True
            return False

def check_company_profile(request, item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
            data=get_passed_profile(user_profile)
            if data=={}:
                return error(request,"Profile Not Found")
        except:
            return error(request,"Profile Not Found")
        if user_profile.last_name!=settings.COMPANY_MESSAGE or user_profile.is_staff or user_profile.is_superuser:
            return error(request,"Profile Not Found")
        image=data.image
        general_announcements=CompanyAnnouncement.objects.filter(company=data.original_user, general_announcement=True).order_by('-announcement_date')
        return render(request,'dashboard/profile_page_company.html',context={"data": data, "image": image, "general_announcements": general_announcements})
    return error_detection(request,1)

def company_change_mode(request,item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
            data=CompanyProfile.objects.get(original_user=user_profile)
            if data=={}:
                return JsonResponse({"error": "Profile Not Found"}, status=400)
            if data.engaged:
                return JsonResponse({"error": "Permission Denied."}, status=400)
        except:
            return JsonResponse({"error": "Profile Not Found"}, status=400)
        if user_profile.last_name!=settings.COMPANY_MESSAGE or user_profile.is_staff or user_profile.is_superuser:
            return JsonResponse({"error": "Profile Not Found"}, status=400)
        try:
            if user_profile!=CompanyProfile.objects.get(user=request.user).original_user:
                return JsonResponse({"error": "Profile Not Found"}, status=400)
            if data.let_staff_manage:
                data.let_staff_manage=False
            else:
                data.let_staff_manage=True
            data.save()
            return JsonResponse({"success": "Done Dana Done"}, status=200)
        except:
            return JsonResponse({"error": "Internal Error"}, status=400)
    return error_detection(request,1)

def check_staff_profile(request,item):
    if error_detection(request,1)==False:
        try:
            user_profile=User.objects.get(id=int(item))
        except:
            return error(request,"Profile Not Found")
        if request.user.is_staff==False:
            return error(request,"Profile Not Found")
        if request.user!=user_profile:
            return error(request,"Profile Not Found")
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
        except:
            StaffPermissions.objects.create(user=request.user)
            permissions=StaffPermissions.objects.get(user=request.user)
        return render(request,'dashboard/profile_page_staff.html',context={"permissions": permissions})
    return error_detection(request,1)

def get_passed_profile(user):
    data={}
    try:
        data=StudentProfile.objects.get(user=user)
    except:
        try:
            data=CompanyProfile.objects.get(user=user)
        except:
            data={}
    return data

def restrict_users(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_ban_users==False and permissions.can_delete_staff_accounts==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        normal_users={}
        if permissions.can_ban_users:
            normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser and permissions.can_delete_staff_accounts:
            staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            staff_users=staff_users.exclude(id=request.user.id)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions})
    return error_detection(request,1)

def get_simple_users(request):
    if request.user.is_staff==False:
        return error(request,"Not a Staff Account")
    users=User.objects.filter(is_staff=False, is_active=True, is_superuser=False)
    for each in users:
        profile=get_the_profile(each)
        if profile=={}:
            users=users.exclude(id=each.id)
        else:
            if profile.account_banned_permanent==True or profile.account_banned_temporary==True:
                users=users.exclude(id=each.id)
    return users

def ban_user_account_permanent(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_ban_users==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        user_ban=User.objects.get(id=int(item))
        if user_ban.is_staff or user_ban.is_superuser:
            return redirect('restrict_users')
        profile=get_the_profile(user_ban)
        if profile=={}:
            return redirect('restrict_users')
        if profile.account_banned_permanent==True:
            return redirect('restrict_users')
        profile.account_banned_permanent=True
        profile.save()
        subject = 'Account Seized'
        message = f'Your account has been banned permanently.<br/>Account is banned by ' + request.user.email + ', contact this email for any query.'
        email=user_ban.email
        Email_thread(subject,message,email).start()
        normal_users={}
        if permissions.can_ban_users:
            normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser and permissions.can_delete_staff_accounts:
            staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            staff_users=staff_users.exclude(id=request.user.id)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions, "code": "1"})
    return error_detection(request,1)

def ban_user_account_temporary(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_ban_users==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        user_ban=User.objects.get(id=int(item))
        if user_ban.is_staff or user_ban.is_superuser:
            return redirect('restrict_users')
        profile=get_the_profile(user_ban)
        if profile=={}:
            return redirect('restrict_users')
        if profile.account_banned_temporary==True:
            return redirect('restrict_users')
        ban_time=settings.TEMORARY_BAN_TIME
        profile.account_banned_temporary=True
        profile.account_ban_time=ban_time
        profile.account_ban_date=datetime.datetime.now()
        profile.save()
        subject = 'Account Seized'
        message = "Your account has been banned temporarily for " + str(ban_time) + " days.<br>Account is banned by " + request.user.email + ", contact this email for any query."
        email=user_ban.email
        Email_thread(subject,message,email).start()
        normal_users={}
        if permissions.can_ban_users:
            normal_users=get_simple_users(request)
        staff_users={}
        if request.user.is_superuser and permissions.can_delete_staff_accounts:
            staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            staff_users=staff_users.exclude(id=request.user.id)
        return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions, "code": "3"})
    return error_detection(request,1)

def delete_staff_account_admin(request,item,type):
    if error_detection(request,1)==False:
        if request.user.is_staff==False or request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_delete_staff_accounts==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            user_del=User.objects.get(id=int(item))
        except:
            return error(request,"User not Found")
        if user_del.is_superuser==True:
            return error(request,"Cannot delete this account")
        if user_del.is_staff==False:
            return error(request,"")
        email=user_del.email
        user_del.delete()
        subject = 'Account Deleted'
        message = f'Your account has been deleted permanently.<br/>Account is deleted by ' + request.user.email + ', contact this email for any query.'
        Email_thread(subject,message,email).start()
        if int(type)==1:
            normal_users={}
            if permissions.can_ban_users:
                normal_users=get_simple_users(request)
            staff_users={}
            if request.user.is_superuser and permissions.can_delete_staff_accounts:
                staff_users=User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
                staff_users=staff_users.exclude(id=request.user.id)
            return render(request,'dashboard1/ban_users.html',context={"normal_users": normal_users, "staff_users": staff_users, "permissions": permissions, "code": "2"})
        if int(type)==2:
            if request.user.is_superuser and permissions.can_manage_staff_accounts:
                users=User.objects.filter(is_staff=True, is_superuser=False)
            return render(request,'dashboard1/manage_staff_accounts.html',context={"permissions": permissions, "data": users, "message": "1 Staff Account deleted"})
    return error_detection(request,1)


def unban_user(request,item):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_unban_users==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if int(item)==0:
            banned_users=get_banned_users(request)
            return render(request,'dashboard1/unban_users.html',context={"banned_users": banned_users, "permissions": permissions})

        try:
            user_unban=User.objects.get(id=int(item))
        except:
            return redirect('unban_user','0')
        if user_unban.is_superuser==True:
            return redirect('unban_user','0')
        if user_unban.is_staff==True:
            return redirect('unban_user','0')
        profile=get_the_profile(user_unban)
        if profile=={}:
            return redirect('unban_user','0')
        if profile.account_banned_temporary==True or profile.account_banned_permanent==True:
            profile.account_banned_temporary=False
            profile.account_banned_permanent=False
            profile.save()
            subject = 'Account Unbanned'
            message = f'Your account has been unbanned.<br/>Account is unbanned by ' + request.user.email + ', contact this email for any query.'
            email=user_unban.email
            Email_thread(subject,message,email).start()
        banned_users=get_banned_users(request)
        return render(request,'dashboard1/unban_users.html',context={"banned_users": banned_users, "permissions": permissions, "success": True})
    return error_detection(request,1)


def get_banned_users(request):
    if request.user.is_superuser==False:
        return error(request,"PAGE NOT FOUND")
    users=User.objects.filter(is_staff=False, is_active=True, is_superuser=False)
    for each in users:
        profile=get_the_profile(each)
        if profile=={}:
            users=users.exclude(id=each.id)
        else:
            if profile.account_banned_permanent==False and profile.account_banned_temporary==False:
                users=users.exclude(id=each.id)
    return users

def create_accounts(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.create_new_accounts==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            form=NewUserForm(request.POST,request.FILES)
            if form.is_valid():
                file=form.cleaned_data['file']
                if str(file).endswith('.csv'):
                    # csv file
                    data=pd.read_csv(file)
                elif str(file).endswith('.xlsx'):
                    # excel file
                    data=pd.read_excel(file)
                else:
                    return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "error": "Not an excel or csv file"})        
                return create_accounts_helper(request,data,permissions)
            return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "error": str(form.errors)})
        else:
            return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions})
    return error_detection(request,1)

def create_accounts_helper(request,data,permissions):
    if 'Email' not in data.columns:
        return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "error": "Email column was not found in the file."})
    if 'Username' not in data.columns:
        return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "error": "Username column was not found in the file."})
    if 'Account Type' not in data.columns:
        return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "error": "Account Type column was not found in the file."})
    cgpa_given=False
    if 'CGPA' in data.columns:
        cgpa_given=True

    total_accounts=len(data['Email'])
    field_with_unknown_values=[]
    field_with_duplicate_data=[]
    for i in range(total_accounts):
        email=data['Email'][i]
        username=data['Username'][i]
        account_type=data['Account Type'][i]
        cgpa=0.0
        if cgpa_given==True:
            try:
                cgpa=float(data['CGPA'][i])
                if cgpa>10.0 or cgpa<0.0:
                    cgpa=0.0
            except:
                cgpa=0.0
            
        if email and username and account_type:
            try:
                User.objects.get(username=username)
                field_with_duplicate_data.append(i+1)
                continue
            except:
                pass
            try:
                User.objects.get(email=email)
                field_with_duplicate_data.append(i+1)
                continue
            except:
                pass
            if account_type!='student' and account_type!='company':
                field_with_unknown_values.append(i+1)
                continue
            password=username + generate_random_password(10)
            user=User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            subject="New account in Clean Frame"
            message="Your email has been used to create "+account_type+" account in Clean Frame. Login Credentials are as follows : \nUsername : "+username+"\nPassword : "+password+"\nPassword is auto generated so it is recommended to change ASAP."
            Email_thread(subject,message,email).start()
            if account_type=="company":
                user.last_name=settings.COMPANY_MESSAGE
                user.save()
            if account_type == "student":
                StudentProfile.objects.create(user=user, verified=True, cgpa=float(cgpa))
            else:
                CompanyProfile.objects.create(user=user, verified=True, original_user=user)
        else:
            field_with_unknown_values.append(i+1)

    if len(field_with_unknown_values)==0 and len(field_with_duplicate_data)==0:
        return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "success": "All accounts have been created successfully."})
    elif len(field_with_unknown_values)==0:
        error="Rows with duplicate data are : "+str(field_with_duplicate_data)+" . You can cross-verify, accounts have been created from rest of the rows."
    elif len(field_with_duplicate_data)==0:
        error="Rows with empty email or empty username or undefined account type are : "+str(field_with_unknown_values)+" . You can cross-verify, accounts have been created from rest of the rows."
    else:
        error1="Rows with duplicate data are : "+str(field_with_duplicate_data)+" ."
        error2="Rows with empty email or empty username or undefined account type are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, accounts have been created from rest of the rows."
        error=error1+"\n"+error2
    return render(request,'dashboard1/create_accounts.html',context={"permissions": permissions, "error": error})

def generate_random_password(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$!"
    password = ""
    for i in range(n) :
        password += digits[math.floor(random.random() * 62)]
    password+='@'
    return password

def manage_blogs(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            pass
        else:
            blogs=Blog.objects.all()
            return render(request,'dashboard1/manage_blogs.html',context={"permissions": permissions, "blogs": blogs})
    return error_detection(request,1)

def manage_sessions(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_sessions==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            name=request.POST.get("session_name")
            try:
                Session.objects.get(name=name)
                return JsonResponse({"error": "Session has been already created with this name."}, status=400)
            except:
                pass
            sessions=Session.objects.filter(active=True)
            for each in sessions:
                each.active=False
                each.save()
            Session.objects.create(name=name)
            profiles=StudentProfile.objects.all()
            for each in profiles:
                if each.got_internship==True:
                    each.got_internship=False
                    each.save()
            return JsonResponse({"success": "Session created"}, status=200)
        sessions=Session.objects.all().order_by('active')
        return render(request,'dashboard1/manage_sessions.html',context={"permissions": permissions, "sessions": sessions})
    return error_detection(request,1)

def manage_sessions_get_result(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_sessions==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            session=Session.objects.get(id=int(item))
        except:
            return error(request,"Session Not Found")
        results=InternshipFinalResult.objects.filter(internship__session=session)
        return render(request,'dashboard1/manage_sessions_get_result.html',context={"permissions": permissions, "session": session, "results": results})
    return error_detection(request,1)

def current_session():
    sessions=Session.objects.filter(active=True)
    if sessions.count()==0:
        return False
    return sessions[0]

def create_new_blog(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            form=BlogForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('manage_blogs')
            else:
                error=form.errors
                return render(request,'dashboard1/new_blog.html',context={"permissions": permissions, "error": error})
        else:
            return render(request,'dashboard1/new_blog.html',context={"permissions": permissions})
    return error_detection(request,1)

def delete_blog(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            Blog.objects.get(id=int(item)).delete()
        except:
            pass
        return redirect('manage_blogs')
    return error_detection(request,1)

def edit_blog(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_blogs==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            blog=Blog.objects.get(id=int(item))
        except:
            return error(request,"Blog not found")
        if request.method=="POST":
            form=BlogForm(request.POST,request.FILES)
            if form.is_valid():
                blog.title=form.cleaned_data['title']
                blog.short_description=form.cleaned_data['short_description']
                blog.brief_description=form.cleaned_data['brief_description']
                if form.cleaned_data['image'] != None:
                    blog.image=form.cleaned_data['image']
                blog.save()
                return redirect('manage_blogs')
            else:
                error=form.errors
                return render(request,'dashboard1/new_blog.html',context={"permissions": permissions, "error": error})
        else:
            return render(request,'dashboard1/edit_blog.html',context={"permissions": permissions, "data": blog})
    return error_detection(request,1)

def manage_staff_accounts(request):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_staff_accounts==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            pass
        else:
            users=User.objects.filter(is_staff=True, is_superuser=False)
            return render(request,'dashboard1/manage_staff_accounts.html',context={"permissions": permissions, "data": users})
    return error_detection(request,1)

def edit_staff_permissions(request, item):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_staff_accounts==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        try:
            staff_data=User.objects.get(id=int(item))
            try:
                data=StaffPermissions.objects.get(user=staff_data)
            except:
                StaffPermissions.objects.create(user=staff_data)
                data=StaffPermissions.objects.get(user=staff_data)
        except:
            return error(request,"Staff Not Found")

        if request.method=="POST":
            data.can_access_student_inactive_accounts=True if request.POST.get('can_access_student_inactive_accounts')=="1" else False
            data.can_access_company_inactive_accounts=True if request.POST.get('can_access_company_inactive_accounts')=="1" else False
            data.can_ban_users=True if request.POST.get('can_ban_users')=="1" else False
            data.can_manage_blogs=True if request.POST.get('can_manage_blogs')=="1" else False
            data.can_manage_technical_support=True if request.POST.get('can_manage_technical_support')=="1" else False
            data.can_give_notifications=True if request.POST.get('can_give_notifications')=="1" else False
            data.can_manage_sessions=True if request.POST.get('can_manage_sessions')=="1" else False
            data.create_new_accounts=True if request.POST.get('can_create_new_accounts')=="1" else False
            data.manage_CGPA=True if request.POST.get('can_manage_cgpa')=="1" else False
            data.remove_students=True if request.POST.get('can_remove_students')=="1" else False
            data.remove_companies=True if request.POST.get('can_remove_companies')=="1" else False
            data.can_manage_internships=True if request.POST.get('can_manage_internships')=="1" else False
            data.save()
            return redirect('edit_staff_permissions',item)
        else:
            return render(request,'dashboard1/edit_staff_permissions.html',context={"permissions": permissions, "data": data, "staff_data": staff_data})
    return error_detection(request,1)

def create_new_staff_account(request):
    if error_detection(request,1)==False:
        if request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_staff_accounts==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            username=request.POST.get('username')
            first_name=request.POST.get('first_name')
            email=request.POST.get('email')
            try:
                user=User.objects.get(email=email)
                return render(request,'dashboard1/new_staff_account.html',context={"permissions": permissions, "error": "Account exists with given email", "username": username, "email": email, "first_name": first_name})
            except:
                try:
                    user=User.objects.get(username=username)
                    return render(request,'dashboard1/new_staff_account.html',context={"permissions": permissions, "error": "Account exists with given username", "username": username, "email": email, "first_name": first_name})
                except:
                    pass
            user=User.objects.create(username=username, email=email, first_name=first_name)
            password=generate_random_password(20)
            user.set_password(password)
            user.is_staff=True
            user.save()
            data=StaffPermissions.objects.create(user=user)
            subject = 'Staff Account created'
            message = f'An staff account has been created for this email in Clean Frame.<br/>Account Details are as follows:<br/>Username: '+str(user)+'<br/>Password: '+str(password)+'<br/>Name: '+str(user.first_name)+'<br/>Now you are a staff, visit the website, login and see what permissions you have been provided with.<br/>The password is a auto generated password so we suggest you to change it.'
            email=email
            Email_thread(subject,message,email).start()
            data.can_access_student_inactive_accounts=True if request.POST.get('can_access_student_inactive_accounts')=="1" else False
            data.can_access_company_inactive_accounts=True if request.POST.get('can_access_company_inactive_accounts')=="1" else False
            data.can_ban_users=True if request.POST.get('can_ban_users')=="1" else False
            data.can_manage_blogs=True if request.POST.get('can_manage_blogs')=="1" else False
            data.can_manage_technical_support=True if request.POST.get('can_manage_technical_support')=="1" else False
            data.can_give_notifications=True if request.POST.get('can_give_notifications')=="1" else False
            data.can_manage_sessions=True if request.POST.get('can_manage_sessions')=="1" else False
            data.create_new_accounts=True if request.POST.get('can_create_new_accounts')=="1" else False
            data.manage_CGPA=True if request.POST.get('can_manage_cgpa')=="1" else False
            data.remove_students=True if request.POST.get('can_remove_students')=="1" else False
            data.remove_companies=True if request.POST.get('can_remove_companies')=="1" else False
            data.can_manage_internships=True if request.POST.get('can_manage_internships')=="1" else False
            data.save()
            return redirect('manage_staff_accounts')
        else:
            return render(request,'dashboard1/new_staff_account.html',context={"permissions": permissions})
    return error_detection(request,1)

def notifications(request):
    if error_detection(request,1)==False:
        try:
            profile=CompanyProfile.objects.get(user=request.user)
            if profile.engaged:
                return error(request,"You don't have permission to access this page")
        except:
            pass
        notifications=Notification.objects.filter(notification_receiver=request.user).order_by('-date')
        if notifications.count()==0:
            notifications="0"
        return render(request,'dashboard1/notifications.html',context={"notifications": notifications, "permissions": get_permissions(request)})
    return error_detection(request,1)

def give_notifications(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_give_notifications==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            message=request.POST.get("message")
            user_id=int(request.POST.get("user_id"))
            if user_id>0:
                try:
                    user=User.objects.get(id=int(user_id))
                except:
                    return error(request,"User not exists")
                Notification.objects.create(notification_sender=request.user, notification_receiver=user, notification=message)
            else:
                if user_id==-1:
                    users=User.objects.filter(is_staff=True, is_superuser=False)
                elif user_id==-2:
                    users=User.objects.filter(is_staff=False, is_superuser=False, last_name=settings.COMPANY_MESSAGE)
                elif user_id==-3:
                    users=User.objects.filter(is_staff=False, is_superuser=False).exclude(last_name=settings.COMPANY_MESSAGE)
                else:
                    return error(request,"URL NOT FOUND")
                for each in users:
                    Notification.objects.create(notification_sender=request.user, notification_receiver=each, notification=message)
            return redirect('give_notifications')
        else:
            data=User.objects.all()
            data=data.exclude(id=request.user.id)
            return render(request,'dashboard1/send_notifications.html',context={"permissions": permissions, "data": data})
    return error_detection(request,1)

def notification_delete(request, item):
    if error_detection(request,1)==False:
        try:
            notification=Notification.objects.get(id=int(item))
        except:
            return redirect('notifications')
        if notification.notification_receiver==request.user:
            notification.delete()
        return redirect('notifications')
    return error_detection(request,1)


def all_chats(request):
    if error_detection(request,1)==False:
        if request.user.is_staff:
            return error(request, "Permission Denied")
        if request.method=="POST":
            chat=request.POST.get('chat')
            ChatRequest.objects.create(user=request.user, message=chat)
            return redirect('all_chats')
        chat_requests=ChatRequest.objects.filter(user=request.user)
        return render(request,"dashboard1/all_chats.html",context={"chats": chat_requests})
    return error_detection(request,1)

def visit_chat(request,item):
    if error_detection(request,1)==False:
        if request.method=="POST":
            pass
        try:
            chat_request=ChatRequest.objects.get(id=int(item))
        except:
            return JsonResponse({"error": "Chat not found."}, status=400)
        if chat_request.user==request.user:
            profile=get_my_profile(request)
            chat_response=ChatResponse.objects.filter(chat_request=chat_request, read=True)
            return render(request,"dashboard1/visit_chat.html",context={"chat_request": chat_request, "chat_response": chat_response, "profile": profile})
        else:
            if request.user.is_staff==False and request.user.is_superuser==False:
                return redirect('home')
            try:
                permissions=StaffPermissions.objects.get(user=request.user)
                if permissions.can_manage_technical_support==False:
                    return error(request,"You don't have permission to access this page")
            except:
                StaffPermissions.objects.create(user=request.user)
                return redirect('dashboard')
            if chat_request.engaged and chat_request.engaged_user!=request.user:
                return error(request,"Chat is already engaged")
            profile=get_the_profile(chat_request.user)
            chat_response=ChatResponse.objects.filter(chat_request=chat_request, read_s=True)
            return render(request,"dashboard1/visit_chat_staff.html",context={"chat_request": chat_request, "chat_response": chat_response, "permissions": get_permissions(request), "profile": profile})
    return error_detection(request,1)

def send_chat(request,item):
    if error_detection(request,1)==False:
        if request.method=="POST":
            pass
        try:
            chat_request=ChatRequest.objects.get(id=int(item))
        except:
            return JsonResponse({"error": "Chat not found."}, status=400)
        if chat_request.chat_ended:
            return JsonResponse({"error": "Chat has been ended."}, status=400)
        if chat_request.user==request.user:
            mess=datetime.datetime.now()
            message=request.GET.get('chat_message')
            mess=mess.strftime("%b")+" "+mess.strftime("%d")+", "+mess.strftime("%Y")+', '+mess.strftime("%I")+':'+mess.strftime("%M")+' '+mess.strftime("%p")
            ChatResponse.objects.create(chat_request=chat_request, responder=request.user, 
                                            username=request.user.username, read=True,
                                            mess_time_str=mess, message=message)
            return JsonResponse({"success": "Chat sent."}, status=200)
        else:
            if request.user.is_staff==False and request.user.is_superuser==False:
                return JsonResponse({"error": "Chat not found."}, status=400)
            try:
                permissions=StaffPermissions.objects.get(user=request.user)
                if permissions.can_manage_technical_support==False:
                    return JsonResponse({"error": "Chat not found."}, status=400)
            except:
                StaffPermissions.objects.create(user=request.user)
                return JsonResponse({"error": "Chat not found."}, status=400)
            if chat_request.engaged and chat_request.engaged_user!=request.user:
                return error(request,"Chat is already engaged")
            mess=datetime.datetime.now()
            message=request.GET.get('chat_message')
            mess=mess.strftime("%b")+" "+mess.strftime("%d")+", "+mess.strftime("%Y")+', '+mess.strftime("%I")+':'+mess.strftime("%M")+' '+mess.strftime("%p")
            ChatResponse.objects.create(chat_request=chat_request, responder=request.user, 
                                            username=request.user.username, read_s=True,
                                            mess_time_str=mess, message=message)
            return JsonResponse({"success": "Chat sent."}, status=200)
    return error_detection(request,1)

def receive_chat(request,item):
    if error_detection(request,1)==False:
        if request.method=="POST":
            pass
        try:
            chat_request=ChatRequest.objects.get(id=int(item))
        except:
            return JsonResponse({"error": "Chat not found."}, status=400)
        if chat_request.chat_ended:
            return JsonResponse({"error": "Chat has been ended."}, status=400)
        if chat_request.user==request.user:
            response=ChatResponse.objects.filter(chat_request=chat_request, read=False)
            for each in response:
                each.read=True
                each.save()
            data=serializers.serialize('json', response)
            return JsonResponse({"success": "message received..", "data": data}, status=200) 
        else:
            if request.user.is_staff==False and request.user.is_superuser==False:
                return JsonResponse({"error": "Chat not found."}, status=400)
            try:
                permissions=StaffPermissions.objects.get(user=request.user)
                if permissions.can_manage_technical_support==False:
                    return JsonResponse({"error": "Chat not found."}, status=400)
            except:
                StaffPermissions.objects.create(user=request.user)
                return JsonResponse({"error": "Chat not found."}, status=400)
            if chat_request.engaged and chat_request.engaged_user!=request.user:
                return error(request,"Chat is already engaged")
            response=ChatResponse.objects.filter(chat_request=chat_request, read_s=False)
            for each in response:
                each.read_s=True
                each.save()
            data=serializers.serialize('json', response)
            return JsonResponse({"success": "message received..", "data": data}, status=200) 
    return error_detection(request,1)

def end_chat(request,item):
    if error_detection(request,1)==False:
        if request.method=="POST":
            pass
        try:
            chat_request=ChatRequest.objects.get(id=int(item))
        except:
            return JsonResponse({"error": "Chat not found."}, status=400)
        if chat_request.user==request.user:
            chat_request.chat_ended=True
            chat_request.save()
            return JsonResponse({"success": "message received.."}, status=200) 
        else:
            if request.user.is_staff==False and request.user.is_superuser==False:
                return JsonResponse({"error": "Chat not found."}, status=400)
            try:
                permissions=StaffPermissions.objects.get(user=request.user)
                if permissions.can_manage_technical_support==False:
                    return JsonResponse({"error": "Chat not found."}, status=400)
            except:
                StaffPermissions.objects.create(user=request.user)
                return JsonResponse({"error": "Chat not found."}, status=400)
            if chat_request.engaged and chat_request.engaged_user!=request.user:
                return error(request,"Chat is already engaged")
            chat_request.chat_ended=True
            chat_request.save()
            return JsonResponse({"success": "message received.."}, status=200) 
    return error_detection(request,1)

def change_chat_mode(request,item):
    if error_detection(request,1)==False:
        if request.method=="POST":
            pass
        try:
            chat_request=ChatRequest.objects.get(id=int(item))
        except:
            return JsonResponse({"error": "Chat not found."}, status=400)
        if chat_request.user==request.user:
            return JsonResponse({"error": "Permission Denied.."}, status=400) 
        else:
            if request.user.is_staff==False and request.user.is_superuser==False:
                return JsonResponse({"error": "Chat not found."}, status=400)
            try:
                permissions=StaffPermissions.objects.get(user=request.user)
                if permissions.can_manage_technical_support==False:
                    return JsonResponse({"error": "Chat not found."}, status=400)
            except:
                StaffPermissions.objects.create(user=request.user)
                return JsonResponse({"error": "Chat not found."}, status=400)
            if chat_request.engaged:
                chat_request.engaged=False
            else:
                chat_request.engaged=True
                chat_request.engaged_user=request.user
            chat_request.save()
            return JsonResponse({"success": "Mode Changed Successfully.."}, status=200)
    return error_detection(request,1)


def technical_support_assist(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_technical_support==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        if request.method=="POST":
            pass
        else:
            support=ChatRequest.objects.all().exclude(user=request.user)
            if support.count()==0:
                support="0"
            return render(request,'dashboard1/assist_technical_support.html',context={"support": support, "permissions": permissions})
    return error_detection(request,1)

def manage_company_internships(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_internships==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        
        company_accounts=CompanyProfile.objects.filter(let_staff_manage=True)
        
        return render(request,'dashboard1/manage_company_internships.html',context={"company_accounts": company_accounts, "permissions": permissions})
    return error_detection(request,1)

def login_as_a_company(request,item):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.can_manage_internships==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        

        try:
            profile=CompanyProfile.objects.get(id=int(item))
        except:
            return error(request,"Profile Not Found")
        if profile.let_staff_manage==False:
            return error(request,"Company does not want you to manage his internships.")
        if profile.engaged==True:
            return error(request,"This account is already engaged.")
        
        profile.engaged=True
        profile.original_user=profile.user
        profile.user2=profile.user
        profile.user=request.user
        profile.is_this_staff_superuser=request.user.is_superuser
        profile.staff_last_name=request.user.last_name
        profile.staff_first_name=request.user.first_name
        profile.save()
        EngagedChecker(str(profile.id)).run()
        user=request.user
        user.is_staff=False
        user.is_superuser=False
        user.last_name=settings.COMPANY_MESSAGE
        user.first_name=profile.user2.first_name
        user.save()
        login(request,profile.user)
        
        return redirect('dashboard')
    return error_detection(request,1)

class EngagedChecker(Thread):
    def __init__(self,profile):
        self.profile=profile
        Thread.__init__(self)

    def run(self):
        turn_off_engaged(self.profile, schedule=120 + int(settings.ENGAGED_EXPIRE_TIME*60))

@background(schedule=10)
def turn_off_engaged(profile):
    profile=CompanyProfile.objects.get(id=int(profile))
    user=profile.user
    user.is_staff=True
    user.is_superuser=profile.is_this_staff_superuser
    user.last_name=profile.staff_last_name
    user.first_name=profile.staff_first_name
    user.save()
    profile.engaged=False
    profile.user=profile.user2
    profile.save()
    

# def still_engaged(profile):
#     old_time=profile.engaged_on
#     profile.engaged_on=datetime.datetime.now()
#     profile.save()
#     new_time=profile.engaged_on
#     profile.engaged_on=old_time
#     profile.save()
#     minutes=((new_time-old_time).total_seconds())/60

#     if minutes<settings.ENGAGED_EXPIRE_TIME:
#         return True
#     return False


def get_all_threads(id):
    threads=[]
    support=TechnicalSupportRequest.objects.get(id=id)
    thread_responses=TechnicalSupportRequest.objects.filter(continued_support=True, main_support_id=support.id).order_by('date')
    threads.append(thread_responses)
    return threads

def delete_account(request):
    if error_detection(request,1)==False:
        try:
            profile=CompanyProfile.objects.get(user=request.user)
            if profile.engaged:
                return error(request,"Permission Denied.")
        except:
            pass
        try:
            u=User.objects.get(username=request.user)
            email=u.email
            subject = 'Account Deletion Notice'
            message = f'Your account has been sucessfully deleted from Clean Frame.<br/>Moreover all the records related are also deleted.<br/>If you create a new account then previous effects or changes would not be shown.'
            SENDMAIL(subject,message,email)            
            u.delete()
        except:
            return error(request,"User Not Found")
    return redirect('home')

def search_users(request):
    if error_detection(request,1)==False:
        if request.method=="POST":
            item=request.POST.get('search')
            usernames=User.objects.filter(is_staff=False, is_superuser=False,username__icontains=item)
            first_names=User.objects.filter(is_staff=False, is_superuser=False,first_name__icontains=item)
            emails=User.objects.filter(is_staff=False, is_superuser=False,email__icontains=item)
            users=usernames | first_names | emails
            if request.user.is_staff==True:
                usernames=User.objects.filter(is_staff=True, username__icontains=item)
                first_names=User.objects.filter(is_staff=True, first_name__icontains=item)
                emails=User.objects.filter(is_staff=True, email__icontains=item)
                users=usernames | first_names | emails | users
            return render(request,"dashboard1/search.html",context={"users": users, "search": item, "total_users": users.count(), "permissions": get_permissions(request)})
        else:
            return redirect('dashboard')
    return error_detection(request,1)


def error(request, message):
    return render(request,"home/error_page.html",context={"error": message})

def remove_students(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.remove_students==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        data=StudentProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        if request.method=="POST":
            form=NewUserForm(request.POST,request.FILES)
            if form.is_valid():
                file=form.cleaned_data['file']
                if str(file).endswith('.csv'):
                    # csv file
                    data1=pd.read_csv(file)
                elif str(file).endswith('.xlsx'):
                    # excel file
                    data1=pd.read_excel(file)
                else:
                    return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data, "new_error": "Not an excel or csv file"})       
                return remove_students_helper(request, data1, permissions, data)
            return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data, "new_error": str(form.errors)})
        else:
            return redirect('student_account_signup_permit')
    return error_detection(request,1)

def remove_students_helper(request, data, permissions, data_to_pass):
    email_given=False
    if 'Email' not in data.columns and 'Username' not in data.columns:
        return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": "Email or Username column was not found in the file."})
    if 'Email' in data.columns:
        email_given=True

    field_on_operation=0
    if email_given:
        field_on_operation=data['Email']
    else:
        field_on_operation=data['Username']

    field_with_unknown_values=[]
    field_with_student_not_found=[]
    for i in range(len(field_on_operation)):
        field=field_on_operation[i]
        if field:
            try:
                user=0
                if email_given:
                    user=User.objects.get(email=field)
                else:
                    user=User.objects.get(username=field)
                if user.is_staff or user.is_superuser or user.last_name==settings.COMPANY_MESSAGE:
                    field_with_student_not_found.append(i+1)
                else:
                    subject="Account Deletion Notice"
                    message="This is to notify that your student account has been deleted by our staff in CleanFrame."
                    Email_thread(subject,message,user.email).start()
                    user.delete()
            except:
                field_with_student_not_found.append(i+1)
        else:
            field_with_unknown_values.append(i+1)
    if len(field_with_unknown_values)==0 and len(field_with_student_not_found)==0:
        return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "success": "All these students were deleted successfully."})
    elif len(field_with_unknown_values)==0:
        error="Rows in which student account was not found are : "+str(field_with_student_not_found)+" . You can cross-verify, and for rest of the rows accounts were deleted."
    elif len(field_with_student_not_found)==0:
        error="Rows with empty email or empty username are : "+str(field_with_unknown_values)+" . You can cross-verify, and for rest of the rows accounts were deleted."
    else:
        error1="Rows in which student account not found are : "+str(field_with_student_not_found)+" ."
        error2="Rows with empty email or empty username  are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, and for rest of the rows accounts were deleted."
        error=error1+"\n"+error2
    return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": error})





def remove_companies(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.remove_companies==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        data=CompanyProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        if request.method=="POST":
            form=NewUserForm(request.POST,request.FILES)
            if form.is_valid():
                file=form.cleaned_data['file']
                if str(file).endswith('.csv'):
                    # csv file
                    data1=pd.read_csv(file)
                elif str(file).endswith('.xlsx'):
                    # excel file
                    data1=pd.read_excel(file)
                else:
                    return render(request,'dashboard/company_accounts.html',context={ "permissions": get_permissions(request), "data": data, "new_error": "Not an excel or csv file"})       
                return remove_companies_helper(request, data1, permissions, data)
            return render(request,'dashboard/company_accounts.html',context={ "permissions": get_permissions(request), "data": data, "new_error": str(form.errors)})
        else:
            return redirect('company_account_signup_permit')
    return error_detection(request,1)

def remove_companies_helper(request, data, permissions, data_to_pass):
    email_given=False
    if 'Email' not in data.columns and 'Username' not in data.columns:
        return render(request,'dashboard/company_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": "Email or Username column was not found in the file."})
    if 'Email' in data.columns:
        email_given=True

    field_on_operation=0
    if email_given:
        field_on_operation=data['Email']
    else:
        field_on_operation=data['Username']

    field_with_unknown_values=[]
    field_with_company_not_found=[]
    for i in range(len(field_on_operation)):
        field=field_on_operation[i]
        if field:
            try:
                user=0
                if email_given:
                    user=User.objects.get(email=field)
                else:
                    user=User.objects.get(username=field)
                if user.is_staff or user.is_superuser or user.last_name!=settings.COMPANY_MESSAGE:
                    field_with_company_not_found.append(i+1)
                else:
                    subject="Account Deletion Notice"
                    message="This is to notify that your company account has been deleted by our staff in CleanFrame."
                    Email_thread(subject,message,user.email).start()
                    user.delete()
            except:
                field_with_company_not_found.append(i+1)
        else:
            field_with_unknown_values.append(i+1)
    if len(field_with_unknown_values)==0 and len(field_with_company_not_found)==0:
        return render(request,'dashboard/company_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "success": "All these companies were deleted successfully."})
    elif len(field_with_unknown_values)==0:
        error="Rows in which company account was not found are : "+str(field_with_company_not_found)+" . You can cross-verify, and for rest of the rows accounts were deleted."
    elif len(field_with_company_not_found)==0:
        error="Rows with empty email or empty username are : "+str(field_with_unknown_values)+" . You can cross-verify, and for rest of the rows accounts were deleted."
    else:
        error1="Rows in which company account not found are : "+str(field_with_company_not_found)+" ."
        error2="Rows with empty email or empty username  are : "+str(field_with_unknown_values)+" .\nYou can cross-verify, and for rest of the rows accounts were deleted."
        error=error1+"\n"+error2
    return render(request,'dashboard/company_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": error})


def upload_cgpa(request):
    if error_detection(request,1)==False:
        if request.user.is_staff==False and request.user.is_superuser==False:
            return redirect('home')
        try:
            permissions=StaffPermissions.objects.get(user=request.user)
            if permissions.manage_CGPA==False:
                return error(request,"You don't have permission to access this page")
        except:
            StaffPermissions.objects.create(user=request.user)
            return redirect('dashboard')
        data=StudentProfile.objects.filter(verified=False, account_banned_permanent=False,  account_banned_temporary=False, user__is_active=True).order_by('signup_date')
        if request.method=="POST":
            form=NewUserForm(request.POST,request.FILES)
            if form.is_valid():
                file=form.cleaned_data['file']
                if str(file).endswith('.csv'):
                    # csv file
                    data1=pd.read_csv(file)
                elif str(file).endswith('.xlsx'):
                    # excel file
                    data1=pd.read_excel(file)
                else:
                    return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data, "new_error": "Not an excel or csv file"})       
                return upload_cgpa_helper(request, data1, permissions, data)
            return render(request,'dashboard/student_accounts.html',context={ "permissions": get_permissions(request), "data": data, "new_error": str(form.errors)})
        else:
            return redirect('student_account_signup_permit')
    return error_detection(request,1)

def upload_cgpa_helper(request, data, permissions, data_to_pass):
    email_given=False
    if 'Email' not in data.columns and 'Username' not in data.columns:
        return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": "Email or Username column was not found in the file."})
    if 'Email' in data.columns:
        email_given=True
    if 'CGPA' not in data.columns:
        return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": "CGPA column was not found in the file."})

    field_on_operation=0
    if email_given:
        field_on_operation=data['Email']
    else:
        field_on_operation=data['Username']

    field_with_unknown_values=[]
    field_with_student_not_found=[]
    for i in range(len(field_on_operation)):
        field=field_on_operation[i]
        cgpa=data["CGPA"][i]
        if field:
            try:
                user=0
                if email_given:
                    user=User.objects.get(email=field)
                else:
                    user=User.objects.get(username=field)
                if user.is_staff or user.is_superuser or user.last_name==settings.COMPANY_MESSAGE:
                    field_with_student_not_found.append(i+1)
                else:
                    if cgpa<0 or cgpa>10:
                        field_with_unknown_values.append(i+1)
                        continue
                    cgpa=float(cgpa)
                    profile=StudentProfile.objects.get(user=user)
                    old_cgpa=profile.cgpa
                    profile.cgpa=cgpa
                    profile.save()
                    subject="CGPA Updated on CleanFrame"
                    message="This is to notify that your CGPA has been updated from " + str(old_cgpa) + " to " + str(cgpa) +" by our staff in CleanFrame."
                    Email_thread(subject,message,user.email).start()
            except:
                field_with_student_not_found.append(i+1)
        else:
            field_with_unknown_values.append(i+1)
    if len(field_with_unknown_values)==0 and len(field_with_student_not_found)==0:
        return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "success": "CV successfully updated for all the students."})
    elif len(field_with_unknown_values)==0:
        error="Rows in which student account was not found are : "+str(field_with_student_not_found)+" . You can cross-verify, and for rest of the rows cgpa was uploaded."
    elif len(field_with_student_not_found)==0:
        error="Rows with empty email or empty username are : "+str(field_with_unknown_values)+" . You can cross-verify, and for rest of the rows cgpa was uploaded."
    else:
        error1="Rows in which student account not found are : "+str(field_with_student_not_found)+" ."
        error2="Rows with empty email or empty username  are : "+str(field_with_unknown_values)+" .\nYou can cross-verify,and for rest of the rows cgpa was uploaded."
        error=error1+"\n"+error2
    return render(request,'dashboard/student_accounts.html',context={ "permissions": permissions, "data": data_to_pass, "new_error": error})