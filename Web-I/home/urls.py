from django.urls import path
from .views import *
# from .views import email
urlpatterns = [
    path('',home,name='home'),
    path('signup/',signup,name='signup'),
    path('signup/verify/<str:code>',signup_verification,name="signup_verification"),
    path('logout/',logout_request,name='logout_request'),
    path('login/',login_request, name='login_request'),
    path('password/forgot/',forgot_password, name="forgot_password"),
    path('password/forgot/confirm/<str:code>',forgot_password_verification,name="forgot_password_verification"),


    path('info/<str:info>',home_,name='home_'),
    
    path('error/<str:message>',error,name="error"),
    #This is to be deleted after final deploy
    path('changepassword/iamastaff/<str:email>/<str:username>',change_staff_only,name="change_staff_only"),
    # path('media/post_images/<str:file>',secureImage,name="secureImage"),
    path('media/post_files/<str:file>',secureFile,name="secureFile"),
    path('query/post/my/',post_query,name="post_query"),

]
